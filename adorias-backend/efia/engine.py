"""
Python port of the Efia chatbot logic from app.js (lines 174-1895).

This is a line-by-line behavioral port of 14 JavaScript modules
(EFIA_DIAGNOSIS_V660 .. EFIA_MULTI_V673) plus the efiaFindProduct /
efiaCatalogueAnswer dispatcher and its legacy keyword-fallback chain.

Design note: in app.js each module is a singleton JS object holding its own
mutable `state`. Here, all of that state lives in one dict (see
`default_state()`) that the Django view loads from/saves to the request
session, so a single browser session gets the same multi-turn memory the
original JS gave a single browser tab. Every method takes the full session
state dict (`self.state`) plus the product list, exactly mirroring how the
original JS modules could reach into `window.EFIA_OTHER_MODULE.state`.
"""
import re
from .category_knowledge import CATEGORY_KNOWLEDGE as CK


def _j(p, keys):
    return " ".join(str(p.get(k)) for k in keys if p.get(k)).lower()


def _uniq(seq):
    return list(dict.fromkeys(seq))


def _num(s):
    try:
        n = float(str(s).replace(",", ""))
        return n
    except (TypeError, ValueError):
        return None


def _fmt_money(n):
    return f"{int(round(n)):,}"


def default_state():
    return {
        "diagnosis": {
            "active": False, "turns": 0, "useCase": "", "budget": None, "experience": "",
            "brand": "", "category": "", "hard": [], "soft": [], "exclusions": [],
            "owned": [], "environment": "", "workflow": "", "lastCandidates": [],
        },
        "precision": {
            "useCase": "", "category": "", "budget": None, "brand": "", "hard": [],
            "owned": [], "turns": 0,
        },
        "modern_advisor": {"history": []},
        "project": {
            "project": "", "uses": [], "budget": None, "space": "", "existing": [],
            "answered": {"budget": False, "space": False, "existing": False},
            "lastQuestion": "",
        },
        "dynamic": {
            "intent": "", "use": "", "budget": None, "experience": "", "owned": [],
            "needs": [], "lastQuestion": "", "turns": 0,
        },
        "human": {"lastIntent": "", "lastUse": "", "lastAnswerType": "", "turns": 0},
        "broad": {"lastIntent": "", "lastProducts": [], "turns": 0},
        "clarify": {
            "topic": "", "use": "", "budget": None, "product": "", "camera": "",
            "people": None, "room": "", "cameras": None, "outputs": "", "operator": "",
            "existing": [], "answered": {}, "asked": [], "turns": 0,
        },
        "multi": {"active": None, "seed": []},
    }


MULTI_DEFINITIONS = {
    "camera": ("Camera", re.compile(r"\b(cameras?|dslr|mirrorless|camcorders?)\b", re.I),
               ["Cameras", "Video Cameras"],
               "Choose the body around the photos or video you need; leave room in the total budget for a lens and the rest of the equipment."),
    "lens": ("Lens", re.compile(r"\b(lenses?|telephoto|wide.angle lens)\b", re.I),
             ["Lenses"],
             "Match the lens mount to the selected camera and choose the view for your subject and available space."),
    "lighting": ("Lighting", re.compile(r"\b(lights?|lighting|softbox(?:es)?|strobes?|flash)\b", re.I),
                 ["Lighting", "Lighting Accessories", "Event & Stage Lighting"],
                 "For a small room, start with one controllable light, a suitable softbox and a stable light stand. Video needs continuous light; still photography can also use flash."),
    "audio": ("Audio", re.compile(r"\b(mics?|microphones?|audio|sound|speakers?|recorders?)\b", re.I),
              ["Audio", "Audio Accessories"],
              "Choose microphones for the number of people speaking and match their connections to the camera, recorder or mixer."),
    "support": ("Tripod / support", re.compile(r"\b(tripods?|monopods?|fluid heads?)\b", re.I),
                ["Camera Support"],
                "Match the support to the combined camera and lens weight; video movement may need a fluid head."),
    "gimbal": ("Gimbal", re.compile(r"\b(gimbals?|stabili[sz]ers?)\b", re.I),
               ["DJI & Creator Gear"],
               "Check both payload and physical balance with the exact camera and lens."),
    "power": ("Power", re.compile(r"\b(batter(?:y|ies)|chargers?|power supplies|dummy battery)\b", re.I),
              ["Batteries & Chargers", "Adapters & Power"],
              "Battery codes, voltage and power connections must match the exact device."),
    "memory": ("Memory / storage", re.compile(r"\b(memory|sd cards?|storage|ssd|hard drives?|card readers?)\b", re.I),
               ["Camera Accessories"],
               "Match the card type and sustained write speed to the camera and recording mode."),
    "production": ("Live production", re.compile(r"\b(switchers?|atem|capture cards?|livestream(?:ing)?|live stream(?:ing)?)\b", re.I),
                   ["Live Production"],
                   "Plan camera outputs, capture or switching, audio, continuous power and the computer or streaming destination together."),
    "cables": ("Cables / connections", re.compile(r"\b(cables?|adapters?|adaptors?)\b", re.I),
               ["Cables & Connectivity", "Adapters & Power"],
               "Confirm both ends of every connection, the signal format and the cable length before selecting cables or adapters."),
    "backgrounds": ("Backgrounds", re.compile(r"\b(backdrops?|backgrounds?)\b", re.I),
                    ["Studio Backgrounds"],
                    "Choose the background width for the room and subject, with a secure support."),
    "printing": ("Printing", re.compile(r"\b(printers?|printing|photo paper)\b", re.I),
                 ["Printing", "Printing & Finishing"],
                 "Match the printer and paper to the print size, expected volume and running costs."),
}

BUDGET_BENCHMARKS = [
    {"keys": ["canon eos r50"], "usd": 679.99, "source": "Canon US"},
    {"keys": ["canon eos r6 mark ii", "canon eos r6 ii"], "usd": 1999.00, "source": "Canon US"},
    {"keys": ["nikon z50 ii", "nikon z50ii"], "usd": 1009.95, "source": "Nikon US"},
    {"keys": ["nikon z5 ii", "nikon z5ii"], "usd": 1599.95, "source": "Nikon US"},
    {"keys": ["nikon z6 ii", "nikon z6ii"], "usd": 1399.95, "source": "Nikon US"},
    {"keys": ["nikon z6 iii", "nikon z6iii"], "usd": 1999.95, "source": "Nikon US"},
    {"keys": ["panasonic lumix gh7", "panasonic gh7"], "usd": 1899.99, "source": "Panasonic US"},
]
BUDGET_FX = {"usdGhs": 11.55, "date": "2026-09-18", "label": "Bank of Ghana reference"}


class EfiaEngine:
    def __init__(self, state, products):
        self.state = state
        self.products = products

    # ================================================================
    # efiaFindProduct(q)  (app.js 174-189)
    # ================================================================
    def find_product(self, q):
        s = (q or "").lower().replace("–", "-").replace("—", "-")
        scored = []
        for p in self.products:
            name = (p.get("name") or "").lower().replace("–", "-").replace("—", "-")
            model = (p.get("model") or "").lower().replace("–", "-").replace("—", "-")
            brand = (p.get("brand") or "").lower()
            score = 0
            if name and name in s:
                score += 100
            if model and len(model) > 3 and model in s:
                score += 80
            tokens = [t for t in re.split(r"[^a-z0-9.]+", name + " " + model) if len(t) > 2]
            score += sum(4 for t in tokens if t in s)
            if brand and brand in s:
                score += 3
            scored.append((score, p))
        scored.sort(key=lambda x: -x[0])
        if scored and scored[0][0] >= 8:
            return scored[0][1]
        return None

    # ================================================================
    # Master dispatcher: efiaCatalogueAnswer(q)  (app.js 190-443)
    # ================================================================
    def answer(self, q):
        combined = self.multi_answer(q)
        if combined:
            return combined

        project_active = bool(self.state["project"]["project"])
        if not project_active:
            clarification = self.clarify_answer(q)
            if clarification:
                return clarification

        school_reply = self.school_answer(q)
        if school_reply:
            return school_reply

        budget_reply = self.budget_answer(q)
        if budget_reply:
            return budget_reply

        broad_reply = self.broad_answer(q)
        if broad_reply:
            return broad_reply

        if self.state["project"]["project"]:
            project_reply = self.project_answer(q)
            if project_reply:
                return project_reply

        human_reply = self.human_answer(q)
        if human_reply:
            return human_reply

        if self.state["project"]["project"]:
            active_project_answer = self.project_answer(q)
            if active_project_answer:
                return active_project_answer

        dynamic_answer = self.dynamic_answer(q)
        if dynamic_answer:
            return dynamic_answer

        project_active = self.state["project"]["project"]
        project_intent = bool(re.search(r"\b(photo studio|photography studio|studio setup|build (?:a|my) studio)\b", q, re.I))
        if project_active or project_intent:
            project_answer = self.project_answer(q)
            if project_answer:
                return project_answer

        modern_answer = self.modern_advisor_answer(q)
        if modern_answer:
            return modern_answer

        customer_answer = self.customer_answer(q)
        if customer_answer:
            return customer_answer

        if self.solution_builder_should_build(q):
            return self.solution_builder_answer(q)

        if self.diagnosis_looks_diagnostic(q):
            return self.precision_answer(q)

        # --- legacy fallback chain (app.js 272-442) ---
        return self._legacy_fallback(q)

    def _legacy_fallback(self, q):
        s = (q or "").lower()

        if re.search(r"blackmagic.*(bmpcc|pocket cinema).*6k|bmpcc.?6k", s) and not re.search(r"g2|pro", s):
            return ("The original Blackmagic Pocket Cinema Camera 6K is the Super 35, active Canon EF-mount "
                    "6K generation. It is different from the later 6K G2 and 6K Pro, so I will not transfer "
                    "G2/Pro battery or feature specifications to it. Tell me the exact lens, media, battery, "
                    "charger or rig item you want to pair with the original 6K.")

        hit = self.find_product(q)
        if hit:
            o = [hit["name"] + ": " + (hit.get("description") or "")]
            if hit.get("specs"):
                o.append("Key details: " + hit["specs"] + ".")
            if hit.get("compatibility"):
                o.append("Compatibility: " + hit["compatibility"])
            if re.search(r"battery|charger|power", s):
                if hit.get("battery"):
                    o.append("Battery: " + hit["battery"] + ".")
                if hit.get("charger"):
                    o.append("Charger/power: " + hit["charger"] + ".")
            status = hit.get("catalogueKnowledgeStatus") or ""
            if status and re.search(r"VERIFY|VARIANT|FAMILY", status):
                o.append("Please confirm your exact camera model and the stocked lens version before purchase.")
            return " ".join(o)

        es, aa, cc = CK["event-stage"], CK["audio-accessories"], CK["cables-connectivity"]
        if re.search(r"moving head|230w beam|strobe|smoke machine|fog machine|4.in.1 par|par light", s):
            if re.search(r"moving|beam", s):
                return es["moving"] + " " + es["safety"]
            if re.search(r"strobe", s):
                return es["strobe"]
            if re.search(r"smoke|fog", s):
                return es["smoke"]
            if re.search(r"par", s):
                return es["par"] + " " + es["safety"]

        if re.search(r"microphone stand|mic stand|podcast boom|boom arm|microphone flag|mic flag|3.5mm audio", s):
            if re.search(r"boom", s):
                return aa["boom"]
            if re.search(r"stand", s):
                return aa["stand"]
            if re.search(r"flag", s):
                return aa["flag"]
            if re.search(r"3.5", s):
                return aa["cable"] + " " + aa["safety"]

        if re.search(r"hdmi cable|sdi cable|mini.hdmi|micro.hdmi", s):
            if re.search(r"mini.hdmi", s):
                return cc["mini"] + " " + cc["safety"]
            if re.search(r"micro.hdmi", s):
                return cc["micro"] + " " + cc["safety"]
            if re.search(r"sdi", s):
                return cc["sdi"] + " " + cc["safety"]
            return cc["hdmi"] + " " + cc["safety"]

        spa = CK["studio-photo-accessories"]
        if re.search(r"green screen|chroma|white background|black background|colored background|backdrop|background clamp|crossbar|light tent|photo box|photo album|passport.photo sleeve|phone holder|super clamp", s):
            if re.search(r"green|chroma", s):
                return spa["green"]
            if re.search(r"backdrop kit", s):
                return spa["kit"] + " " + spa["safety"]
            if re.search(r"background|backdrop", s):
                return spa["background"] + " " + spa["safety"]
            if re.search(r"crossbar|pole", s):
                return spa["crossbar"]
            if re.search(r"light tent|photo box", s):
                return spa["lighttent"]
            if re.search(r"phone holder", s):
                return spa["phone"]
            if re.search(r"clamp", s):
                return spa["clamp"] + " " + spa["safety"]
            if re.search(r"album|passport.photo sleeve", s):
                return spa["album"]
            return spa["summary"] + " " + spa["safety"]

        pp = CK["printing-photo"]
        if re.search(r"printer|printing|epson l805|epson l1800|epson l3258|selphy|photo paper|refill ink|laminat|passport photo cutter|35.?45|50.?50", s):
            if re.search(r"ink|refill", s):
                return pp["ink"] + " " + pp["safety"]
            if re.search(r"selphy", s):
                return pp["selphy"]
            if re.search(r"paper", s):
                return pp["paper"]
            if re.search(r"laminat", s):
                return pp["laminate"]
            if re.search(r"passport|35.?45|50.?50", s):
                return pp["passport"]
            if re.search(r"printer|epson", s):
                return pp["printer"] + " " + pp["summary"]
            return pp["summary"] + " " + pp["safety"]

        ca = CK["camera-accessories"]
        if re.search(r"camera bag|backpack|shoulder bag|video.camera bag|hard case|protective case|uv filter|lens hood|lens cap|body cap|cleaning kit|blower|camera strap", s):
            if re.search(r"bag|backpack", s):
                return ca["bags"] + " " + ca["safety"]
            if re.search(r"hard case|protective case|waterproof", s):
                return ca["hardcase"] + " " + ca["safety"]
            if re.search(r"uv filter|filter size", s):
                return ca["filter"]
            if re.search(r"hood", s):
                return ca["hood"]
            if re.search(r"cap", s):
                return ca["cap"]
            if re.search(r"clean|blower", s):
                return ca["cleaning"]
            if re.search(r"strap", s):
                return ca["strap"]
            return ca["summary"] + " " + ca["safety"]

        ap = CK["adapters-power"]
        if re.search(r"dummy battery|ac adapter|lens adapter|ef.to.rf|ef to rf|ef.to.ef.m|ef to ef-m|viltrox adapter|sony adapter", s):
            if re.search(r"dummy|ac adapter", s):
                return ap["dummy"] + " " + ap["safety"]
            if re.search(r"ef.to.rf|ef to rf|eos r adapter", s):
                return ap["efrf"]
            if re.search(r"ef.to.ef.m|ef to ef-m|ef-m adapter", s):
                return ap["efm"]
            if re.search(r"sony", s):
                return ap["sony"] + " " + ap["safety"]
            if re.search(r"viltrox", s):
                return ap["viltrox"] + " " + ap["safety"]
            return ap["summary"] + " " + ap["safety"]

        ms = CK["memory-storage"]
        if re.search(r"sd card|memory card|compactflash|compact flash|\bcf card|card reader|external ssd|storage|sandisk|128gb", s):
            if re.search(r"compactflash|compact flash|\bcf card", s):
                return ms["cf"]
            if re.search(r"reader", s):
                return ms["reader"]
            if re.search(r"ssd", s):
                return ms["ssd"]
            if re.search(r"sandisk|128gb", s):
                return ms["sandisk"] + " " + ms["safety"]
            if re.search(r"speed|4k|video|record", s):
                return ms["speed"] + " " + ms["sd"] + " " + ms["safety"]
            if re.search(r"capacity|gb|how many", s):
                return ms["capacity"]
            return ms["summary"] + " " + ms["safety"]

        bc = CK["batteries-chargers"]
        if re.search(r"battery|batteries|charger|charging|lp-e|bp-828|np-fw50|vbd58|vb26|f970|fv100", s):
            if re.search(r"charger|charging", s):
                return bc["charger"] + " " + bc["safety"]
            if re.search(r"camcorder|xa\d|xf\d|hxr|pxw|handycam", s):
                return bc["camcorder"] + " " + bc["safety"]
            if re.search(r"camera|canon|nikon|sony|panasonic|blackmagic", s):
                return bc["camera"] + " " + bc["safety"]
            if re.search(r"spare|extra", s):
                return bc["spare"]
            return bc["summary"] + " " + bc["safety"]

        dj = CK["dji-creator"]
        if re.search(r"dji|mavic|rs 4|rs4|osmo|rc pro|dji mic|drone|camera gimbal|phone gimbal", s):
            if re.search(r"mavic|drone", s):
                return dj["drone"] + " " + dj["safety"]
            if re.search(r"rs 4|rs4|camera gimbal", s):
                return dj["gimbal"]
            if re.search(r"mobile 7|phone gimbal", s):
                return dj["phone"]
            if re.search(r"pocket", s):
                return dj["pocket"]
            if re.search(r"rc pro|controller", s):
                return dj["controller"]
            if re.search(r"mic", s):
                return dj["mic"]
            return dj["summary"]

        cs = CK["camera-support"]
        if re.search(r"tripod|monopod|fluid head|fluid-head|camera cage|shoulder rig|slider|quick.release|quick release|ball head|tripod head|weifeng", s):
            if re.search(r"video|fluid", s):
                return cs["video"] + " " + cs["payload"]
            if re.search(r"quick.release|quick release|plate", s):
                return cs["qr"]
            if re.search(r"cage|rig", s):
                return cs["cage"]
            if re.search(r"slider", s):
                return cs["slider"]
            if re.search(r"phone", s):
                return cs["phone"]
            if re.search(r"load|payload|heavy", s):
                return cs["payload"] + " " + cs["safety"]
            return cs["summary"] + " " + cs["safety"]

        lp = CK["live-production"]
        if re.search(r"atem|avmatrix|live production|livestream|live stream|video switcher|capture device|capture card|hdmi splitter|wireless hdmi|field monitor|video monitor|teleprompter|sdi", s):
            if re.search(r"iso", s):
                return lp["iso"]
            if re.search(r"switcher|atem|avmatrix", s):
                return lp["switcher"] + " " + lp["design"]
            if re.search(r"capture", s):
                return lp["capture"]
            if re.search(r"splitter", s):
                return lp["splitter"]
            if re.search(r"hdmi|sdi", s):
                return lp["hdmisdi"]
            if re.search(r"wireless", s):
                return lp["wireless"]
            if re.search(r"monitor", s):
                return lp["monitor"]
            if re.search(r"teleprompter", s):
                return lp["teleprompter"]
            return lp["summary"] + " " + lp["design"]

        ak = CK["audio"]
        if re.search(r"microphone|\bmic\b|audio|wireless mic|recorder|zoom h5|zoom h6|zoom h8|sm7b|mv7|boya|sennheiser|xlr|phantom|podcast", s):
            if re.search(r"wireless|wm8|sennheiser|ew 135", s):
                return ak["wireless"] + " " + ak["safety"]
            if re.search(r"recorder|zoom h5|zoom h6|zoom h8", s):
                return ak["recorder"]
            if re.search(r"usb|xlr|mv7", s):
                return ak["usbxlr"]
            if re.search(r"phantom", s):
                return ak["phantom"]
            if re.search(r"gain|preamp|sm7b", s):
                return ak["gain"] + " " + ak["dynamic"]
            if re.search(r"camera", s):
                return ak["camera"]
            return ak["summary"] + " Tell me what you are recording and what camera, computer, mixer or interface you will connect it to."

        la = CK["lighting-accessories"]
        if re.search(r"softbox|octabox|umbrella|reflector|c-stand|c stand|light stand|boom stand|backdrop|background stand|honeycomb|grid|snoot|barn door|gel|diffuser|sandbag|clamp|bowens", s):
            if re.search(r"softbox|octabox", s):
                return la["softbox"] + " " + la["safety"]
            if re.search(r"grid|honeycomb", s):
                return la["grid"]
            if re.search(r"umbrella", s):
                return la["umbrella"]
            if re.search(r"c-stand|c stand", s):
                return la["cstand"] + " " + la["stand"]
            if re.search(r"stand|sandbag", s):
                return la["stand"]
            if re.search(r"bowens", s):
                return la["bowens"]
            if re.search(r"snoot|barn door|diffuser|gel", s):
                return la["control"]
            if re.search(r"backdrop|background", s):
                return la["background"]
            return la["summary"]

        lk = CK["lighting"]
        if re.search(r"flash|speedlight|strobe|lighting|light |led|softbox|ring light|godox|yongnuo|ttl|trigger|xpro|x3-|sl60|sl150|sl200|sl300|lc500", s):
            if re.search(r"flash.*continuous|continuous.*flash|video light|for video", s):
                return lk["flashcontinuous"]
            if re.search(r"ttl|manual flash", s):
                return lk["ttl"]
            if re.search(r"trigger|transmitter|xpro|x3-", s):
                return lk["trigger"]
            if re.search(r"softbox|modifier|bowens", s):
                return lk["modifiers"]
            if re.search(r"rgb|bi.color|daylight|colour|color", s):
                return lk["color"]
            if re.search(r"ring light", s):
                return lk["ring"]
            return lk["summary"] + " Tell me your camera model and whether this is for photos, video, livestreaming or studio work."

        k = CK["lenses"]
        if re.search(r"lens|lenses|mount|adapter|ef |rf |nikon f|nikon z|ftz|portrait|aperture|f\/1|f\/2|f\/4|prime|zoom", s):
            if re.search(r"canon| ef | rf |eos", " " + s):
                return k["canon"]
            if re.search(r"nikon|nikkor|ftz| z6| z5| d850| d750", s):
                return k["nikon"]
            if re.search(r"portrait", s):
                return k["portraits"] + " Tell me your camera model and I can narrow down the compatible Adorias options."
            if re.search(r"aperture|f\/1|f\/2|f\/4", s):
                return k["aperture"]
            if re.search(r"prime|zoom", s):
                return k["primezoom"]
            if re.search(r"aps-c|dx|full.frame|format", s):
                return k["format"]
            return k["summary"] + " Tell me the exact camera model and what you shoot, and I can guide you without guessing the mount."

        return ""

    # ================================================================
    # EFIA_DIAGNOSIS_V660  (app.js 578-732)
    # ================================================================
    def diagnosis_text(self, p):
        return _j(p, ["name", "brand", "model", "description", "specs", "keySpecifications",
                      "compatibility", "useCases", "battery", "chargerPower", "category", "originalCategory"])

    def diagnosis_extract(self, q):
        st = self.state["diagnosis"]
        s = q.lower()
        st["turns"] += 1
        if re.search(r"\b(beginner|new to|first camera|first time|don't know|dont know|not sure)\b", s):
            st["experience"] = "beginner"
        if re.search(r"\b(professional|expert|experienced|advanced)\b", s):
            st["experience"] = "advanced"

        budget = re.search(r"(?:gh[₵c]?\s*|g(h)?s?\s*|budget(?:\s+is|\s+of)?\s*)?(\d[\d,]{2,})\s*(?:ghs|cedis?)?", s, re.I)
        if budget and re.search(r"\b(budget|ghs|cedi|₵|around|under|below|max|maximum)\b", s, re.I):
            st["budget"] = _num(budget.group(2))

        use_cases = [
            ("church", "church"), ("livestream", "livestreaming"), ("live stream", "livestreaming"),
            ("youtube", "YouTube"), ("vlog", "vlogging"), ("wedding", "weddings"),
            ("portrait", "portraits"), ("sports", "sports"), ("event", "events"),
            ("podcast", "podcasting"), ("interview", "interviews"), ("studio", "studio"),
            ("wildlife", "wildlife"), ("cinema", "cinema/video production"), ("photo", "photography"),
        ]
        for k, v in use_cases:
            if k in s:
                st["useCase"] = v

        for b in ["canon", "nikon", "sony", "panasonic", "blackmagic", "godox", "dji", "boya", "sennheiser", "shure"]:
            if re.search(r"\b" + b + r"\b", s, re.I):
                st["brand"] = b

        categories = [
            ("camera", "cameras-video"), ("camcorder", "cameras-video"), ("lens", "lenses"),
            ("light", "lighting"), ("microphone", "audio"), ("mic ", "audio"),
            ("tripod", "camera-support"), ("gimbal", "dji-creator"), ("battery", "batteries-chargers"),
            ("charger", "batteries-chargers"), ("memory", "memory-storage"), ("sd card", "memory-storage"),
            ("switcher", "live-production"), ("atem", "live-production"),
        ]
        for k, v in categories:
            if k in s:
                st["category"] = v

        hard_patterns = [
            ("4k", "4K"), ("xlr", "XLR"), ("sdi", "SDI"), ("3g-sdi", "3G-SDI"),
            ("usb streaming", "USB streaming"), ("usb-c", "USB-C"), ("full frame", "full-frame"),
            ("aps-c", "APS-C"), ("micro four thirds", "Micro Four Thirds"),
            ("e-mount", "E-mount"), ("rf mount", "RF mount"), ("long recording", "long recording"),
            ("dual card", "dual card slots"), ("dual sd", "dual SD slots"),
        ]
        for k, v in hard_patterns:
            if k in s and v not in st["hard"]:
                st["hard"].append(v)

        own = re.search(r"(?:i (?:already )?(?:have|own)|we (?:already )?(?:have|own))\s+([^.!?]+)", s, re.I)
        if own and own.group(1).strip() not in st["owned"]:
            st["owned"].append(own.group(1).strip())

        pref = re.search(r"(?:prefer|would like|ideally)\s+([^.!?]+)", s, re.I)
        if pref and pref.group(1).strip() not in st["soft"]:
            st["soft"].append(pref.group(1).strip())

        no = re.search(r"(?:don't want|dont want|do not want|avoid|no )\s+([^.!?]+)", s, re.I)
        if no and no.group(1).strip() not in st["exclusions"]:
            st["exclusions"].append(no.group(1).strip())

        if re.search(r"\b(indoor|indoors)\b", s):
            st["environment"] = "indoor"
        if re.search(r"\b(outdoor|outdoors)\b", s):
            st["environment"] = "outdoor"
        if re.search(r"\b(handheld|run and gun|run-and-gun)\b", s):
            st["workflow"] = "handheld"
        if re.search(r"\b(tripod|fixed camera)\b", s):
            st["workflow"] = "tripod/fixed"

    def diagnosis_looks_diagnostic(self, q):
        return bool(re.search(
            r"\b(i need|i want|recommend|suggest|best for|suitable|setup|beginner|not sure|what should|"
            r"which camera|which lens|livestream|youtube|vlog|wedding|church|podcast|interview)\b", q, re.I))

    def diagnosis_question(self):
        s = self.state["diagnosis"]
        if not s["useCase"]:
            return "What will you mainly use the equipment for—for example photography, YouTube, weddings, church livestreaming, interviews, events, or something else?"
        if not s["category"] and not re.search(r"livestream|church|youtube|vlog|wedding|portrait|sports|cinema|photo", s["useCase"], re.I):
            return "What type of equipment are you looking for: camera, lens, lighting, audio, tripod/support, livestream equipment, or a complete setup?"
        if not s["experience"]:
            return "Are you a beginner, or are you already comfortable choosing camera and production equipment?"
        if not s["budget"]:
            return "Do you have a budget range? You can also say “no fixed budget” if you want me to focus on suitability first."
        if not s["workflow"] and re.search(r"livestream|church|youtube|wedding|interview|cinema", s["useCase"], re.I):
            return "Will this mostly be handheld/mobile, tripod-based, or a mixture of both?"
        if not s["owned"]:
            return "Do you already own any cameras, lenses, batteries, chargers, microphones, tripods, or other equipment that the new setup should work with?"
        return ""

    def diagnosis_candidates(self):
        s = self.state["diagnosis"]

        def keep(p):
            if s["category"] and p.get("category") != s["category"]:
                return False
            if s["brand"] and (p.get("brand") or "").lower() != s["brand"]:
                return False
            t = self.diagnosis_text(p)
            for x in s["exclusions"]:
                if x.lower() in t:
                    return False
            return True

        pool = [p for p in self.products if keep(p)]
        use_tokens = [x for x in re.split(r"\W+", (s["useCase"] + " " + " ".join(s["hard"])).lower()) if len(x) > 2]

        scored = []
        for p in pool:
            t = self.diagnosis_text(p)
            score, matched, missing = 0, [], []
            if s["brand"] and (p.get("brand") or "").lower() == s["brand"]:
                score += 12
            for h in s["hard"]:
                words = [w for w in re.split(r"\W+", h.lower()) if w]
                ok = all(w in t for w in words)
                if ok:
                    score += 15
                    matched.append(h)
                else:
                    missing.append(h)
            for tok in use_tokens:
                if tok in t:
                    score += 2
            for pref in s["soft"]:
                if pref.lower() in t:
                    score += 3
            scored.append({"p": p, "score": score, "matched": matched, "missing": missing})

        scored = [x for x in scored if not s["hard"] or not x["missing"]]
        scored.sort(key=lambda x: (-x["score"], x["p"]["name"]))
        return scored[:3]

    def diagnosis_explain(self, c):
        p = c["p"]
        reasons = []
        if self.state["diagnosis"]["brand"] and (p.get("brand") or "").lower() == self.state["diagnosis"]["brand"]:
            reasons.append("matches your preferred brand")
        if c["matched"]:
            reasons.append("matches " + ", ".join(c["matched"]))
        use_case = self.state["diagnosis"]["useCase"]
        if use_case and use_case.lower() in self.diagnosis_text(p):
            reasons.append("catalogue information explicitly aligns with " + use_case)
        if not reasons:
            reasons.append("is one of the closest catalogue matches to the requirements provided")
        model_suffix = f" ({p['model']})" if p.get("model") and p["model"] not in p["name"] else ""
        compat = f" Compatibility: {p['compatibility']}" if p.get("compatibility") else ""
        power = " / ".join(x for x in [p.get("battery"), p.get("chargerPower")] if x)
        power_txt = f" Power: {power}." if power else ""
        return f"• {p['name']}{model_suffix} — {'; '.join(reasons)}.{power_txt}{compat}"

    def diagnosis_answer(self, q):
        self.diagnosis_extract(q)
        st = self.state["diagnosis"]
        st["active"] = True
        follow = self.diagnosis_question()
        if follow and st["turns"] <= 3 and not st["hard"]:
            return f"I can help you build the right Adorias setup. {follow}"
        cs = self.diagnosis_candidates()
        st["lastCandidates"] = [x["p"]["sku"] for x in cs]
        if not cs:
            hard_note = f" ({', '.join(st['hard'])})" if st["hard"] else ""
            return f"I don't have a catalogue match that satisfies all the requirements you've given me{hard_note}. {follow or 'Which requirement can be flexible, if any?'}"
        out = "Here are the options I’d consider:\n\n" + "\n\n".join(self.diagnosis_explain(x) for x in cs)
        if follow:
            out += f"\n\nTo narrow this down further: {follow}"
        else:
            out += "\n\nI can also build the supporting lens, battery/charger, memory, tripod, audio, lighting and livestream accessories around the option you choose, using verified catalogue compatibility where available."
        return out

    # ================================================================
    # EFIA_PRECISION_V662  (app.js 749-842)
    # ================================================================
    def precision_extract(self, q):
        st = self.state["precision"]
        s = q.lower()
        st["turns"] += 1
        use = [
            ("church", "church livestreaming"), ("livestream", "livestreaming"), ("live stream", "livestreaming"),
            ("youtube", "YouTube"), ("vlog", "vlogging"), ("wedding", "weddings"), ("interview", "interviews"),
            ("sports", "sports"), ("portrait", "portraits"), ("podcast", "podcasting"), ("event", "events"),
        ]
        for k, v in use:
            if k in s:
                st["useCase"] = v
        if re.search(r"\b(camera|camcorder|dslr|mirrorless)\b", s) or re.search(r"livestream|church|vlog|wedding|portrait|sports", s):
            st["category"] = "cameras-video"
        if re.search(r"\b(lens|focal|zoom lens|prime lens)\b", s):
            st["category"] = "lenses"
        if re.search(r"\b(microphone|mic|audio recorder)\b", s):
            st["category"] = "audio"
        if re.search(r"\b(light|softbox|led panel)\b", s):
            st["category"] = "lighting"
        bm = (re.search(r"(?:budget(?:\s+(?:is|of))?|under|below|maximum|max|around)\s*(?:gh[₵c]?|ghs)?\s*([\d,]+)", s, re.I)
              or re.search(r"(?:gh[₵c]?|ghs)\s*([\d,]+)", s, re.I)
              or re.search(r"([\d,]+)\s*(?:ghs|cedis?)", s, re.I))
        if bm:
            st["budget"] = _num(bm.group(1))
        for b in ["canon", "nikon", "sony", "panasonic", "blackmagic"]:
            if re.search(r"\b" + b + r"\b", s):
                st["brand"] = b
        req = [("xlr", "xlr"), ("sdi", "sdi"), ("4k", "4k"), ("aps-c", "aps-c"), ("full frame", "full frame"),
               ("e-mount", "e-mount"), ("dual card", "dual card"), ("usb streaming", "usb streaming")]
        for k, v in req:
            if k in s and v not in st["hard"]:
                st["hard"].append(v)
        own = re.search(r"(?:already (?:have|own)|i (?:have|own)|we (?:have|own))\s+([^.!?]+)", s, re.I)
        if own and own.group(1).strip() not in st["owned"]:
            st["owned"].append(own.group(1).strip())

    def precision_txt(self, p):
        return _j(p, ["name", "brand", "model", "originalCategory", "category", "description", "specs",
                      "keySpecifications", "compatibility", "useCases", "battery", "chargerPower"])

    def precision_valid_product(self, p):
        st = self.state["precision"]
        if st["category"]:
            if st["category"] == "cameras-video":
                category_ok = p.get("category") in ["cameras-video", "Cameras & Video"]
            else:
                category_ok = p.get("category") == st["category"]
            if not category_ok:
                return False
        if st["category"] == "cameras-video" and p.get("originalCategory") not in ["Cameras", "Video Cameras"]:
            return False
        if st["brand"] and (p.get("brand") or "").lower() != st["brand"]:
            return False
        return True

    def precision_evidence_score(self, p):
        t = self.precision_txt(p)
        s = self.state["precision"]
        score, reasons = 0, []
        if s["useCase"]:
            live = bool(re.search(r"livestream|church", s["useCase"]))
            if live:
                if re.search(r"hdmi|sdi|usb streaming|live production|video", t):
                    score += 12
                    reasons.append("video/live-output capability is documented")
                if re.search(r"camcorder|video cameras", t):
                    score += 8
                    reasons.append("purpose-built video form factor")
                if re.search(r"xlr", t):
                    score += 4
                    reasons.append("professional audio connectivity is documented")
            for tok in [x for x in re.split(r"\W+", s["useCase"]) if len(x) > 3]:
                if tok.lower() in t:
                    score += 2
        for h in s["hard"]:
            if h in t:
                score += 18
                reasons.append("matches " + h)
            else:
                return None
        if s["brand"] and (p.get("brand") or "").lower() == s["brand"]:
            score += 8
            reasons.append("matches requested brand")
        if p.get("sourceUrl") or p.get("specSource"):
            score += 2
        if p.get("compatibility"):
            score += 1
        return {"p": p, "score": score, "reasons": reasons}

    def precision_candidates(self):
        pool = [p for p in self.products if self.precision_valid_product(p)]
        scored = [self.precision_evidence_score(p) for p in pool]
        scored = [x for x in scored if x]
        scored.sort(key=lambda x: (-x["score"], x["p"]["name"]))
        return scored[:3]

    def precision_missing_question(self):
        s = self.state["precision"]
        if not s["useCase"]:
            return "What will you mainly use it for?"
        if not s["category"]:
            return "What type of equipment are you choosing?"
        if re.search(r"livestream|church", s["useCase"]) and not s["owned"]:
            return "What livestream equipment do you already have—for example an ATEM/capture device, computer, lenses, microphones or tripods?"
        return ""

    def precision_answer(self, q):
        self.precision_extract(q)
        s = self.state["precision"]
        ask = self.precision_missing_question()
        if not s["category"]:
            return "I can diagnose this with you. " + ask
        cs = self.precision_candidates()
        if not cs:
            label = "camera/video" if s["category"] == "cameras-video" else s["category"]
            return f"I don't have a verified {label} match that satisfies every requirement you gave me. I won't substitute an unrelated product. {ask}"
        intro = ("For church livestreaming, I’m prioritizing documented video/output capability and practical "
                 "production use—not photography-only features.") if re.search(r"livestream|church", s["useCase"]) \
            else "Here are the options I’d consider."
        option_lines = []
        for i, x in enumerate(cs):
            p = x["p"]
            why = "; ".join(x["reasons"]) if x["reasons"] else "good fit based on the available product information"
            spec = p.get("keySpecifications") or p.get("specs") or p.get("description") or ""
            option_lines.append(f"{i+1}. {p['name']} — {why}. {spec}")
        options = "\n\n".join(option_lines)
        budget = ""
        if s["budget"]:
            budget = (f"\n\nYour stated budget is GHS {_fmt_money(s['budget'])}. Our catalogue does not yet "
                      "contain reliable current selling prices, so I will not falsely claim that any option is "
                      "within budget. Once current prices are connected, I can enforce that limit exactly.")
        nxt = (f"\n\nTo make the recommendation precise: {ask}" if ask else
               "\n\nI can now build the compatible livestream chain around your preferred camera: lens, "
               "continuous power/batteries, tripod, audio, capture/switcher and cabling, using verified catalogue compatibility.")
        return intro + "\n\n" + options + budget + nxt

    # ================================================================
    # EFIA_SOLUTION_BUILDER_V663  (app.js 849-948)
    # ================================================================
    SOLUTION_CATEGORY_LABELS = {
        "cameras-video": "Camera / Video", "lenses": "Lens", "batteries-chargers": "Power",
        "camera-support": "Tripod / Support", "audio": "Audio", "live-production": "Live Production",
        "cables-connectivity": "Cabling", "memory-storage": "Memory / Storage", "lighting": "Lighting",
    }

    def solution_txt(self, p):
        return _j(p, ["name", "brand", "model", "description", "specs", "keySpecifications", "compatibility",
                      "useCases", "battery", "chargerPower", "originalCategory", "category"])

    def solution_is_verified_enough(self, p):
        status = (p.get("catalogueKnowledgeStatus") or "").lower()
        return bool(p.get("sourceUrl") or p.get("specSource") or re.search(r"verified|manufacturer provenance|inventory confirmed", status))

    def solution_score(self, p, ctx, role):
        t = self.solution_txt(p)
        n, why = 0, []
        if not self.solution_is_verified_enough(p):
            n -= 3
        if ctx.get("brand") and (p.get("brand") or "").lower() == ctx["brand"]:
            n += 4
            why.append("matches the preferred brand")
        if re.search(r"church|livestream", ctx.get("useCase") or ""):
            if re.search(r"hdmi|sdi|capture|switcher|atem|video|livestream", t):
                n += 5
                why.append("relevant to a livestream workflow")
            if role == "audio" and re.search(r"microphone|wireless|xlr|audio", t):
                n += 4
                why.append("supports production audio")
            if role == "camera-support" and re.search(r"tripod|fluid|video", t):
                n += 4
                why.append("suited to stable video support")
            if role == "batteries-chargers" and re.search(r"charger|battery|power", t):
                n += 3
                why.append("supports camera power")
            if role == "live-production" and re.search(r"atem|capture|switcher|hdmi", t):
                n += 6
                why.append("supports switching/capture")
        return {"p": p, "score": n, "why": why}

    def solution_compatible_accessory(self, p, primary, role):
        a = self.solution_txt(p)
        c = self.solution_txt(primary)
        if role == "batteries-chargers":
            batt = (primary.get("battery") or "").lower()
            if not batt:
                return {"ok": False, "note": "camera battery compatibility is not documented strongly enough"}
            tokens = re.findall(r"\b(?:lp-[a-z0-9]+|np-[a-z0-9]+|bp-[a-z0-9]+|dmw-[a-z0-9-]+)\b", batt, re.I)
            return {"ok": any(x.lower() in a for x in tokens), "note": "battery model must match the camera record"}
        if role == "lenses":
            mounts = ["e-mount", "rf mount", "ef mount", "micro four thirds", "f mount", "z mount"]
            mount = next((x for x in mounts if x in c), None)
            if not mount:
                return {"ok": False, "note": "lens mount is not sufficiently documented"}
            return {"ok": mount in a, "note": "lens mount must match"}
        return {"ok": True, "note": "workflow-level match; exact ports/cables should still be confirmed"}

    def solution_best(self, role, ctx, primary):
        pool = [p for p in self.products if p.get("category") == role and (not primary or p.get("sku") != primary.get("sku"))]
        if primary and role in ["batteries-chargers", "lenses"]:
            pool = [p for p in pool if self.solution_compatible_accessory(p, primary, role)["ok"]]
        scored = sorted((self.solution_score(p, ctx, role) for p in pool), key=lambda x: (-x["score"], x["p"]["name"]))
        return scored[0] if scored else None

    def solution_camera(self, ctx):
        cs = self.precision_candidates()
        return cs[0]["p"] if cs else None

    def solution_build(self, ctx):
        primary = self.solution_camera(ctx)
        if not primary:
            return {"error": "I couldn't identify a sufficiently supported camera/video starting point from the requirements provided."}
        roles = ["lenses", "batteries-chargers", "camera-support", "audio", "live-production", "cables-connectivity", "memory-storage"]
        items = [{"role": "cameras-video", "p": primary, "essential": True, "why": ["primary camera/video choice from the diagnosis"]}]
        for role in roles:
            x = self.solution_best(role, ctx, primary)
            if x:
                items.append({"role": role, "p": x["p"],
                              "essential": role in ["batteries-chargers", "camera-support", "live-production", "cables-connectivity"],
                              "why": x["why"]})
            elif role in ["lenses", "batteries-chargers"]:
                label = self.SOLUTION_CATEGORY_LABELS[role]
                items.append({"role": role, "p": None, "essential": True,
                              "warning": f"No {label} item was added because exact compatibility is not sufficiently documented in the catalogue."})
        return {"primary": primary, "items": items}

    def solution_format(self, ctx, result):
        if result.get("error"):
            return result["error"]
        lines = []
        for x in result["items"]:
            label = self.SOLUTION_CATEGORY_LABELS.get(x["role"], x["role"])
            if not x["p"]:
                lines.append(f"• {label} — VERIFY BEFORE SALE: {x['warning']}")
                continue
            tag = "ESSENTIAL" if x["essential"] else "OPTION / WORKFLOW DEPENDENT"
            why = "; ".join(x["why"]) if x.get("why") else "suitable workflow option"
            lines.append(f"• {label} — {x['p']['name']} [{tag}]\n  Why: {why}.")
        return (f"Here is a first-pass Adorias system built around {result['primary']['name']}. I separated "
                "essentials from workflow-dependent items and refused to guess lens/power compatibility where "
                "the catalogue does not prove it.\n\n" + "\n\n".join(lines) +
                "\n\nBefore purchase, Efia should confirm camera count, shooting distance, available lighting, "
                "audio source count, existing switcher/capture hardware, cable run lengths and whether the stream "
                "goes to a computer or standalone encoder.")

    def solution_builder_should_build(self, q):
        return bool(re.search(
            r"\b(complete setup|full setup|whole setup|build (?:me )?(?:a|the) setup|everything i need|"
            r"full system|livestream chain|church setup|what else do i need)\b", q, re.I))

    def solution_builder_answer(self, q):
        self.precision_extract(q)
        ctx = self.state["precision"]
        return self.solution_format(ctx, self.solution_build(ctx))

    # ================================================================
    # EFIA_CUSTOMER_ANSWER_V664  (app.js 976-1045)
    # ================================================================
    def customer_text(self, p):
        return _j(p, ["name", "brand", "model", "description", "keySpecifications", "specs", "compatibility",
                      "useCases", "battery", "chargerPower", "originalCategory"])

    def customer_use_profile(self, q):
        s = q.lower()
        if re.search(r"\b(sport|sports|football|soccer|basketball|athletics|wildlife|action)\b", s):
            return {"name": "sports", "priorities": ["autofocus", "continuous shooting", "reach", "video"], "category": "cameras-video"}
        if re.search(r"\b(church|livestream|live stream)\b", s):
            return {"name": "livestream", "priorities": ["video output", "long-form use", "audio", "power"], "category": "cameras-video"}
        if re.search(r"\b(vlog|youtube|creator)\b", s):
            return {"name": "creator", "priorities": ["autofocus", "video", "portable"], "category": "cameras-video"}
        return None

    def customer_score_sports(self, p):
        t = self.customer_text(p)
        s, pros, cons = 0, [], []
        if re.search(r"mirrorless|dslr|camera", t):
            s += 5
        if re.search(r"autofocus|dual pixel|af\b", t):
            s += 5
            pros.append("autofocus capability is documented")
        if re.search(r"4k", t):
            s += 2
            pros.append("4K video is documented")
        if re.search(r"full.frame", t):
            s += 2
            pros.append("full-frame body")
        if re.search(r"aps-c", t):
            s += 2
            pros.append("APS-C body can be useful when extra field-of-view reach is wanted")
        if re.search(r"camcorder", t):
            s -= 2
            cons.append("less photography-oriented than an interchangeable-lens stills camera")
        if not re.search(r"lens|mount|e-mount|rf|ef mount|f mount|z mount|micro four thirds", t):
            cons.append("lens/reach choice still needs to be confirmed")
        return {"score": s, "pros": pros, "cons": cons}

    def customer_candidates(self, q):
        profile = self.customer_use_profile(q)
        if not profile:
            return []
        if profile["category"] == "cameras-video":
            pool = [p for p in self.products if p.get("category") in ["cameras-video", "Cameras & Video"]
                    and p.get("originalCategory") in ["Cameras", "Video Cameras"]]
        else:
            pool = [p for p in self.products if p.get("category") == profile["category"]]
        scored = []
        for p in pool:
            if profile["name"] == "sports":
                r = self.customer_score_sports(p)
                scored.append({"p": p, "score": r["score"], "pros": r["pros"], "cons": r["cons"]})
            else:
                base = self.precision_evidence_score(p) or {"score": 0, "reasons": []}
                scored.append({"p": p, "score": base.get("score") or 0, "pros": base.get("reasons") or [], "cons": []})
        scored.sort(key=lambda x: (-x["score"], x["p"]["name"]))
        return scored[:3]

    def customer_accessory_advice(self, use):
        if use == "sports":
            return {"essentials": ["A lens with enough reach for your shooting distance", "Spare battery / reliable power", "Fast, compatible memory card"],
                    "optional": ["Monopod or tripod for long-lens work", "External microphone if recording match/event audio", "Protective bag and cleaning kit"]}
        if use == "livestream":
            return {"essentials": ["Continuous/reliable power", "Stable tripod/support", "Correct capture/switcher connection and cabling"],
                    "optional": ["External audio system", "Monitor", "Backup battery and memory"]}
        return {"essentials": ["Compatible power and memory"], "optional": ["Tripod/support", "Audio or lighting as the job requires"]}

    def customer_answer(self, q):
        self.precision_extract(q)
        profile = self.customer_use_profile(q)
        if not profile:
            return None
        cs = self.customer_candidates(q)
        if not cs:
            return "I don't have enough verified catalogue information to give you a reliable option yet."
        intro = "For sports, these are the camera options I’d look at first:" if profile["name"] == "sports" \
            else "These are the options I’d consider first:"
        option_lines = []
        for i, x in enumerate(cs):
            pros = "; ".join(x["pros"][:2]) if x["pros"] else "strong catalogue fit for this use"
            cons = x["cons"][0] if x["cons"] else "exact lens/accessory choice depends on your setup"
            option_lines.append(f"{i+1}. {x['p']['name']}\n   Pros: {pros}.\n   Consider: {cons}.")
        options = "\n\n".join(option_lines)
        a = self.customer_accessory_advice(profile["name"])
        return (f"{intro}\n\n{options}\n\nEssentials: {' • '.join(a['essentials'])}."
                f"\n\nOptional: {' • '.join(a['optional'])}.")

    # ================================================================
    # EFIA_MODERN_ADVISOR_V665  (app.js 1052-1133)
    # ================================================================
    def modern_text(self, p):
        return _j(p, ["name", "brand", "model", "originalCategory", "description", "keySpecifications", "specs", "compatibility", "useCases"])

    def modern_profile(self, q):
        s = q.lower()
        if re.search(r"\b(wedding|weddings|bridal|event shoot|event photography)\b", s):
            return {"use": "wedding", "title": "For wedding shoots, I’d start with these:", "preferBodies": True}
        if re.search(r"\b(sport|sports|football|soccer|basketball|action)\b", s):
            return {"use": "sports", "title": "For sports, I’d start with these:", "preferBodies": True}
        if re.search(r"\b(portrait|portraits)\b", s):
            return {"use": "portrait", "title": "For portraits, I’d start with these:", "preferBodies": True}
        if re.search(r"\b(vlog|youtube|creator)\b", s):
            return {"use": "creator", "title": "For YouTube / creator work, I’d start with these:", "preferBodies": True}
        return None

    def modern_score(self, p, prof):
        t = self.modern_text(p)
        n, pros, cons = 0, [], []
        body = bool(re.search(r"cameras", p.get("originalCategory") or "", re.I))
        video = bool(re.search(r"video cameras", p.get("originalCategory") or "", re.I))
        if prof["preferBodies"] and body:
            n += 18
        if prof["preferBodies"] and video:
            n -= 8
        if re.search(r"mirrorless", t):
            n += 10
            pros.append("modern mirrorless system")
        if re.search(r"dslr", t):
            n += 7
            pros.append("DSLR system with broad photographic use")
        if re.search(r"full.frame", t):
            n += 7
            pros.append("full-frame body")
        if re.search(r"autofocus|dual pixel|af\b", t):
            n += 4
            pros.append("documented autofocus features")
        if re.search(r"4k", t):
            n += 3
            pros.append("4K video for hybrid photo/video coverage")
        if re.search(r"dual (sd|card)|two card", t):
            n += 5
            pros.append("dual-card capability is useful for event redundancy")
        if prof["use"] == "wedding":
            if re.search(r"portrait|wedding|event|low.light", t):
                n += 6
                pros.append("catalogue information aligns with event/people shooting")
            if video:
                cons.append("camcorder-first design; better when wedding video is the priority rather than still photography")
        if prof["use"] == "sports":
            if re.search(r"continuous|burst|sports|action", t):
                n += 7
                pros.append("catalogue information supports action-oriented shooting")
            if re.search(r"aps-c", t):
                n += 2
                pros.append("APS-C format can be practical when extra field-of-view reach is useful")
        if not pros:
            pros.append("interchangeable-lens camera option from the Adorias range")
        if not re.search(r"dual (sd|card)|two card", t) and prof["use"] == "wedding":
            cons.append("confirm card-backup workflow before paid event use")
        if not re.search(r"lens|mount|rf|e-mount|z mount|f mount|micro four thirds", t):
            cons.append("choose the lens based on venue size and shooting distance")
        return {"p": p, "score": n, "pros": _uniq(pros), "cons": _uniq(cons)}

    def modern_rank(self, q):
        prof = self.modern_profile(q)
        if not prof:
            return None
        pool = [p for p in self.products if p.get("category") == "cameras-video" and p.get("originalCategory") in ["Cameras", "Video Cameras"]]
        ranked = sorted((self.modern_score(p, prof) for p in pool), key=lambda x: (-x["score"], x["p"]["name"]))
        history = self.state["modern_advisor"]["history"]
        picked, brands = [], {}
        for x in ranked:
            repeat = x["p"]["sku"] in history
            brand = (x["p"].get("brand") or "").lower()
            if repeat and len(picked) < 2:
                continue
            if brands.get(brand, 0) >= 2:
                continue
            picked.append(x)
            brands[brand] = brands.get(brand, 0) + 1
            if len(picked) == 3:
                break
        if len(picked) < 3:
            for x in ranked:
                if x not in picked and len(picked) < 3:
                    picked.append(x)
        history.extend(x["p"]["sku"] for x in picked)
        self.state["modern_advisor"]["history"] = history[-12:]
        return {"prof": prof, "picked": picked}

    def modern_accessories(self, use):
        if use == "wedding":
            return {"essentials": ["A suitable fast/versatile lens for the venue", "Spare batteries", "Reliable memory cards"],
                    "optional": ["Flash/lighting for receptions", "Second camera body for backup", "Tripod/monopod for ceremony or video", "External microphone if recording video"]}
        if use == "sports":
            return {"essentials": ["A lens with enough reach", "Spare batteries", "Fast compatible memory"],
                    "optional": ["Monopod for long lenses", "Second body", "Weather protection where needed"]}
        return {"essentials": ["Compatible lens", "Spare power", "Memory"], "optional": ["Support", "Lighting/audio as required"]}

    def modern_format(self, result):
        prof, picked = result["prof"], result["picked"]
        cards = []
        for i, x in enumerate(picked):
            pros = "\n".join("✓ " + v for v in x["pros"][:3])
            cons_list = x["cons"] if x["cons"] else ["Exact lens choice depends on the job"]
            cons = "\n".join("• " + v for v in cons_list[:2])
            cards.append(f"━━━━━━━━━━━━━━━━━━━━\n{i+1}. {x['p']['name']}\n\nWHY IT WORKS\n{pros}\n\nKEEP IN MIND\n{cons}")
        a = self.modern_accessories(prof["use"])
        return (f"{prof['title']}\n\n" + "\n\n".join(cards) +
                f"\n\n━━━━━━━━━━━━━━━━━━━━\nESSENTIALS\n" +
                "\n".join("• " + v for v in a["essentials"]) +
                "\n\nOPTIONAL / NICE TO HAVE\n" + "\n".join("• " + v for v in a["optional"]))

    def modern_advisor_answer(self, q):
        r = self.modern_rank(q)
        return self.modern_format(r) if r else None

    # ================================================================
    # EFIA_PROJECT_V666  (app.js 1138-1253)
    # ================================================================
    def project_extract(self, q):
        st = self.state["project"]
        s = q.lower()
        if re.search(r"\b(photo studio|photography studio|studio setup|build (?:a|my) studio)\b", s):
            st["project"] = "photo-studio"
        use_map = [("birthday", "birthdays"), ("wedding", "weddings"), ("baby shower", "baby showers"),
                   ("portrait", "portraits"), ("personal", "personal portraits"), ("passport", "passport photos"),
                   ("product", "product photography"), ("fashion", "fashion")]
        for k, v in use_map:
            if k in s and v not in st["uses"]:
                st["uses"].append(v)

        bm = (re.search(r"(?:budget(?:\s+(?:is|of))?|under|around|max(?:imum)?)\s*(?:ghs|gh₵|ghc|₵)?\s*([\d,]+)", s, re.I)
              or re.search(r"(?:ghs|gh₵|ghc|₵)\s*([\d,]+)", s, re.I)
              or re.search(r"([\d,]+)\s*(?:ghs|cedis?)", s, re.I))
        if bm:
            st["budget"] = _num(bm.group(1))
            st["answered"]["budget"] = True
        if re.search(r"\b(no fixed budget|budget is flexible|flexible budget)\b", s):
            st["budget"] = None
            st["answered"]["budget"] = True

        sm = re.search(r"\b(?:room|studio|space)\s*(?:is|about|around)?\s*(\d+(?:\.\d+)?)\s*(?:x|by)\s*(\d+(?:\.\d+)?)\s*(m|metres?|meters?|ft|feet)?", s, re.I)
        if sm:
            st["space"] = f"{sm.group(1)} × {sm.group(2)} {sm.group(3) or ''}".strip()
            st["answered"]["space"] = True
        sizematch = re.search(r"\b(small|medium|large)\s+(?:room|studio|space)\b", s)
        if sizematch:
            st["space"] = sizematch.group(0)
            st["answered"]["space"] = True

        if re.search(r"\b(i|we) (?:already )?(?:have|own)\b", s):
            st["existing"].append(q.strip())
            st["answered"]["existing"] = True
        if re.search(r"\b(starting from scratch|have nothing|own nothing|don't have anything|do not have anything)\b", s):
            st["answered"]["existing"] = True

        last_q = st["lastQuestion"]
        if last_q == "budget" and not st["answered"]["budget"] and re.search(r"\d", s):
            n = re.search(r"[\d,]+", s)
            if n:
                st["budget"] = _num(n.group(0))
                st["answered"]["budget"] = True
        if last_q == "space" and not st["answered"]["space"] and len(q.strip()) < 80:
            st["space"] = q.strip()
            st["answered"]["space"] = True
        if last_q == "existing" and not st["answered"]["existing"]:
            st["existing"].append(q.strip())
            st["answered"]["existing"] = True
        return st

    def project_next_question(self):
        st = self.state["project"]
        if not st["answered"]["budget"]:
            st["lastQuestion"] = "budget"
            return "What budget would you like me to build the studio around?"
        if not st["answered"]["space"]:
            st["lastQuestion"] = "space"
            return "Roughly how large is the shooting space? Even “small room”, “medium studio” or dimensions are enough."
        if not st["answered"]["existing"]:
            st["lastQuestion"] = "existing"
            return "What equipment do you already own—camera, lenses, flashes/lights, stands or backgrounds? You can also say “starting from scratch”."
        st["lastQuestion"] = ""
        return ""

    def project_txt(self, p):
        return _j(p, ["name", "brand", "model", "originalCategory", "category", "description", "keySpecifications", "specs", "compatibility", "useCases"])

    def project_camera_score(self, p):
        t = self.project_txt(p)
        n, pros, cons = 0, [], []
        if p.get("originalCategory") != "Cameras":
            return None
        if re.search(r"mirrorless", t):
            n += 12
            pros.append("mirrorless body suits a modern photo/hybrid workflow")
        if re.search(r"dslr", t):
            n += 9
            pros.append("DSLR body remains practical for event and portrait photography")
        if re.search(r"full.frame", t):
            n += 9
            pros.append("full-frame body")
        if re.search(r"autofocus|dual pixel|af\b", t):
            n += 5
            pros.append("documented autofocus capability")
        if re.search(r"4k", t):
            n += 2
            pros.append("also supports hybrid photo/video work")
        if re.search(r"dual (sd|card)|two card", t):
            n += 5
            pros.append("dual-card capability can add event redundancy")
        if re.search(r"portrait|wedding|event|studio", t):
            n += 5
            pros.append("catalogue knowledge aligns with people/event work")
        if not re.search(r"dual (sd|card)|two card", t):
            cons.append("confirm the preferred backup/card workflow for paid events")
        if not re.search(r"lens|mount|rf|e-mount|z mount|f mount|micro four thirds", t):
            cons.append("lens choice should be matched to portraits, groups and venue size")
        return {"p": p, "score": n, "pros": _uniq(pros), "cons": _uniq(cons)}

    def project_camera_options(self):
        ranked = [x for x in (self.project_camera_score(p) for p in self.products) if x]
        ranked.sort(key=lambda x: (-x["score"], x["p"]["name"]))
        out, seen_families, brand_count = [], set(), {}
        for x in ranked:
            family = re.sub(r"\s+", " ", re.sub(r"\b(mark|ii|iii|iv|v|2|3|4)\b", "", (x["p"].get("name") or "").lower())).strip()
            brand = (x["p"].get("brand") or "").lower()
            if family in seen_families or brand_count.get(brand, 0) >= 2:
                continue
            seen_families.add(family)
            brand_count[brand] = brand_count.get(brand, 0) + 1
            out.append(x)
            if len(out) == 3:
                break
        return out

    def project_find_category(self, category, keywords=()):
        pool = [p for p in self.products if p.get("category") == category]
        scored = []
        for p in pool:
            t = self.project_txt(p)
            score = sum(3 for k in keywords if k in t)
            scored.append((score, p))
        scored.sort(key=lambda x: (-x[0], x[1]["name"]))
        return scored[0][1] if scored else None

    def project_build_studio(self):
        st = self.state["project"]
        cams = self.project_camera_options()
        lens = self.project_find_category("lenses", ["portrait", "24-70", "50mm", "85mm", "zoom"])
        lighting = self.project_find_category("lighting", ["flash", "strobe", "softbox", "studio"])
        support = self.project_find_category("camera-support", ["tripod", "stand"])
        memory = self.project_find_category("memory-storage", ["extreme pro", "sd"])
        bg = self.project_find_category("studio-photo-accessories", ["background", "backdrop"])
        return {"st": st, "cams": cams, "lens": lens, "lighting": lighting, "support": support, "memory": memory, "bg": bg}

    def project_format(self, result):
        st, cams = result["st"], result["cams"]
        lens, lighting, support, memory, bg = result["lens"], result["lighting"], result["support"], result["memory"], result["bg"]
        camera_blocks = []
        for i, x in enumerate(cams):
            pros = "\n".join(f"✓ {v}" for v in x["pros"][:3])
            note = x["cons"][0] if x["cons"] else "Match the lens to your shooting distance and style."
            camera_blocks.append(f"{i+1}. {x['p']['name']}\n{pros}\nConsider: {note}")
        essentials = [
            f"Lens — {lens['name']}" if lens else "Lens — choose portrait + group coverage after confirming camera mount",
            f"Lighting — {lighting['name']}" if lighting else "Lighting — studio flash/continuous lighting setup",
            f"Background — {bg['name']}" if bg else "Background/backdrop system",
            f"Support — {support['name']}" if support else "Light stands / camera support",
            f"Memory — {memory['name']}" if memory else "Reliable compatible memory cards",
            "Spare camera power / batteries",
        ]
        uses = ", ".join(st["uses"]) if st["uses"] else "portrait and event photography"
        budget_line = (f"Budget noted: GHS {_fmt_money(st['budget'])}. I won’t claim the setup fits that "
                        "amount until current Adorias selling prices are connected.") if st["budget"] else ""
        return (f"For {uses}, I’d build this as a PHOTO studio first—not a camcorder setup.\n\n"
                "CAMERA OPTIONS\n\n" + "\n\n".join(camera_blocks) +
                "\n\nSTUDIO ESSENTIALS\n" + "\n".join("• " + v for v in essentials) +
                "\n\nOPTIONAL AS YOU GROW\n• Second camera body for paid-event backup\n• Additional flash/light and modifiers\n• Reflector\n• Extra backgrounds\n• Wireless trigger where compatible\n• Storage/backup drive\n\n" +
                budget_line)

    def project_answer(self, q):
        st = self.project_extract(q)
        if st["project"] != "photo-studio":
            return None
        ask = self.project_next_question()
        if ask:
            uses = ", ".join(st["uses"]) if st["uses"] else "your shoots"
            return f"A photo studio for {uses} makes sense. {ask}"
        return self.project_format(self.project_build_studio())

    # ================================================================
    # EFIA_DYNAMIC_V667  (app.js 1258-1340)
    # ================================================================
    def dynamic_extract(self, q):
        st = self.state["dynamic"]
        s = q.lower()
        st["turns"] += 1
        intents = [
            ("photo-studio", r"\b(photo studio|photography studio|studio setup)\b"),
            ("camera", r"\b(camera|dslr|mirrorless)\b"),
            ("livestream", r"\b(livestream|live stream|church stream|streaming)\b"),
            ("audio", r"\b(podcast|microphone|mic|audio recorder|wireless mic)\b"),
            ("lighting", r"\b(light|lighting|softbox|flash|strobe)\b"),
            ("live-production", r"\b(atem|switcher|capture card|video switcher)\b"),
        ]
        for v, pat in intents:
            if re.search(pat, s):
                st["intent"] = v
        uses = [
            ("wedding", r"\b(weddings?|bridal)\b"), ("sports", r"\b(sport|football|soccer|basketball|action)\b"),
            ("portrait", r"\b(portraits?|headshots?|family|kids?|children)\b"), ("wildlife", r"\b(wildlife|birds?)\b"),
            ("creator", r"\b(youtube|vlog|creator)\b"), ("interview", r"\b(interview)\b"),
            ("event", r"\b(events?|birthdays?|baby showers?|graduations?|ceremon(?:y|ies))\b"),
            ("product", r"\b(product photography|product shoot)\b"), ("church", r"\b(church|worship)\b"),
        ]
        for v, pat in uses:
            if re.search(pat, s):
                st["use"] = v
        bm = re.search(r"(?:budget|under|around|max(?:imum)?)\D{0,12}([\d,]+)", s, re.I) or re.search(r"(?:ghs|ghc|₵)\s*([\d,]+)", s, re.I)
        if bm:
            st["budget"] = _num(bm.group(1))
        if re.search(r"\b(beginner|new to|first camera)\b", s):
            st["experience"] = "beginner"
        if re.search(r"\b(pro|professional|experienced)\b", s):
            st["experience"] = "experienced"
        own = re.search(r"(?:already have|already own|i have|we have)\s+([^.!?]+)", s, re.I)
        if own:
            st["owned"].append(own.group(1).strip())
        return st

    def dynamic_category_for(self, st):
        if st["intent"] in ["camera", "livestream", "photo-studio"] or st["use"] in ["wedding", "sports", "portrait", "wildlife", "creator", "event", "product"]:
            return "cameras-video"
        if st["intent"] == "audio":
            return "audio"
        if st["intent"] == "lighting":
            return "lighting"
        if st["intent"] == "live-production":
            return "live-production"
        return ""

    def dynamic_text(self, p):
        return _j(p, ["name", "brand", "model", "originalCategory", "category", "description", "keySpecifications", "specs", "compatibility", "useCases"])

    def dynamic_camera_rank(self, st):
        pool = [p for p in self.products if p.get("category") in ["cameras-video", "Cameras & Video"] and p.get("originalCategory") == "Cameras"]
        out = []
        for p in pool:
            t = self.dynamic_text(p)
            score, pros, cons = 0, [], []
            if re.search(r"mirrorless", t):
                score += 9
                pros.append("modern mirrorless system")
            if re.search(r"dslr", t):
                score += 6
                pros.append("DSLR system")
            if re.search(r"full.frame", t):
                score += 6
                pros.append("full-frame body")
            if re.search(r"autofocus|dual pixel|af\b", t):
                score += 4
                pros.append("documented autofocus capability")
            if re.search(r"4k", t):
                score += 3
                pros.append("4K video capability")
            if re.search(r"dual (sd|card)|two card", t):
                score += 4
                pros.append("dual-card capability")
            use = st.get("use")
            if use in ("sports", "wildlife"):
                if re.search(r"continuous|burst|action|sports", t):
                    score += 8
                    pros.append("action-oriented capability is documented")
                if re.search(r"aps-c", t):
                    score += 2
            if use in ("wedding", "portrait", "event"):
                if re.search(r"portrait|wedding|event|studio|people", t):
                    score += 6
            if use == "creator":
                if re.search(r"vlog|creator|selfie|usb|stream", t):
                    score += 8
                    pros.append("creator-oriented features are documented")
            if use == "product":
                if re.search(r"studio|detail|high resolution|megapixel", t):
                    score += 4
            if not re.search(r"lens|mount|rf|e-mount|z mount|f mount|micro four thirds", t):
                cons.append("confirm the best lens for the job")
            out.append({"p": p, "score": score, "pros": _uniq(pros), "cons": cons})
        out.sort(key=lambda x: (-x["score"], x["p"]["name"]))
        return out

    def dynamic_diverse(self, lst, n=3):
        out, brands = [], {}
        for x in lst:
            b = (x["p"].get("brand") or "").lower()
            if brands.get(b, 0) >= 2:
                continue
            out.append(x)
            brands[b] = brands.get(b, 0) + 1
            if len(out) == n:
                break
        return out

    def dynamic_accessories(self, use):
        m = {
            "wedding": {"e": ["Versatile/fast lens", "Spare batteries", "Reliable memory cards"], "o": ["Flash/lighting", "Second body", "Tripod/monopod", "Audio for video"]},
            "sports": {"e": ["Telephoto/reach-appropriate lens", "Spare batteries", "Fast compatible memory"], "o": ["Monopod", "Second body", "Weather protection"]},
            "wildlife": {"e": ["Long lens", "Spare batteries", "Fast compatible memory"], "o": ["Monopod/tripod", "Weather protection", "Extra storage"]},
            "portrait": {"e": ["Portrait-appropriate lens", "Lighting or reflector", "Spare battery/memory"], "o": ["Backgrounds", "Wireless trigger", "Second light"]},
            "creator": {"e": ["Suitable lens", "Reliable power", "Memory"], "o": ["Microphone", "Tripod/gimbal", "Lighting"]},
            "event": {"e": ["Versatile lens", "Spare power", "Memory"], "o": ["Flash", "Backup body", "Audio"]},
            "product": {"e": ["Suitable lens", "Controlled lighting", "Tripod/support"], "o": ["Light tent/background", "Reflectors", "Tether/storage workflow"]},
        }
        return m.get(use, {"e": ["Compatible lens", "Power", "Memory"], "o": ["Support", "Lighting/audio as needed"]})

    def dynamic_format_camera(self, st):
        picks = self.dynamic_diverse(self.dynamic_camera_rank(st))
        if not picks:
            return None
        title = f"For {st['use']}, I’d compare these first:" if st.get("use") else "I’d compare these camera options first:"
        blocks = []
        for i, x in enumerate(picks):
            pros = x["pros"][:3] if x["pros"] else ["strong interchangeable-lens option from the Adorias range"]
            pros_txt = "\n".join("✓ " + v for v in pros)
            cons = x["cons"][0] if x["cons"] else "lens choice and workflow should be matched to the job"
            blocks.append(f"{i+1}. {x['p']['name']}\n{pros_txt}\nConsider: {cons}")
        a = self.dynamic_accessories(st.get("use"))
        return (f"{title}\n\n" + "\n\n".join(blocks) +
                "\n\nESSENTIALS\n" + "\n".join("• " + v for v in a["e"]) +
                "\n\nOPTIONAL\n" + "\n".join("• " + v for v in a["o"]))

    def dynamic_answer(self, q):
        st = self.dynamic_extract(q)
        if st["intent"] == "photo-studio":
            return self.project_answer(q)
        cat = self.dynamic_category_for(st)
        if cat == "cameras-video":
            return self.dynamic_format_camera(st)
        return None

    # ================================================================
    # EFIA_HUMAN_V668  (app.js 1345-1426)
    # ================================================================
    HUMAN_DETECT_RULES = [
        ("lens", r"\b(lens|lenses|50mm|85mm|24-70|70-200|wide angle|telephoto)\b"),
        ("audio", r"\b(mics?|microphones?|podcast|wireless (?:audio|mics?|microphones?)|recorder|voice over|voiceover)\b"),
        ("lighting", r"\b(lights?|lighting|softbox(?:es)?|flash|strobe|led panel|key light)\b"),
        ("live-production", r"\b(atem|switcher|capture card|capture device|multi.?camera|multicam)\b"),
        ("support", r"\b(tripod|monopod|fluid head|slider|camera support)\b"),
        ("power", r"\b(battery|batteries|charger|continuous power|dummy battery)\b"),
        ("memory", r"\b(memory card|sd card|storage|ssd|hard drive|card reader)\b"),
        ("gimbal", r"\b(gimbal|stabilizer|stabiliser|dji rs)\b"),
        ("printing", r"\b(printer|photo paper|passport photo|print photos|printing)\b"),
        ("studio", r"\b(photo studio|photography studio|studio setup|build .*studio)\b"),
        ("camera", r"\b(camera|dslr|mirrorless|camcorder)\b"),
    ]
    HUMAN_USE_RULES = [
        ("church", r"\b(church|worship|ministry)\b"), ("wedding", r"\b(weddings?|bridal)\b"),
        ("sports", r"\b(sports?|football|soccer|basketball|action)\b"), ("wildlife", r"\b(wildlife|birds?)\b"),
        ("portrait", r"\b(portraits?|headshots?|family photos?|family|kids?|children)\b"),
        ("creator", r"\b(youtube|vlog|creator|tiktok)\b"), ("podcast", r"\b(podcast|voice over|voiceover)\b"),
        ("interview", r"\b(interviews?)\b"),
        ("event", r"\b(events?|birthdays?|baby showers?|concert|graduations?|ceremon(?:y|ies))\b"),
        ("product", r"\b(product photography|product shoot)\b"),
    ]
    HUMAN_ALIASES = {
        "lens": (["lenses", "Lenses"]), "audio": (["audio", "Audio"]), "lighting": (["lighting", "Lighting & Studio"]),
        "live-production": (["live-production", "Live Production"]), "support": (["camera-support", "Tripods & Support"]),
        "power": (["batteries-chargers", "Accessories"]), "memory": (["memory-storage", "Accessories"]),
        "gimbal": (["dji-creator", "Drones & Gimbals"]), "printing": (["printing-photo", "Printing & Photo"]),
    }

    def human_detect(self, q):
        s = q.lower()
        intent = ""
        for v, pat in self.HUMAN_DETECT_RULES:
            if re.search(pat, s):
                intent = v
                break
        use = ""
        for v, pat in self.HUMAN_USE_RULES:
            if re.search(pat, s):
                use = v
                break
        if not intent and use in ["wedding", "sports", "wildlife", "portrait", "creator", "event", "product"]:
            intent = "camera"
        return {"intent": intent, "use": use, "s": s}

    def human_catalogue(self, category):
        a = self.HUMAN_ALIASES.get(category, [])

        def keep(p):
            if p.get("category") in a:
                return True
            oc = (p.get("originalCategory") or "").lower()
            if category == "support" and re.search(r"camera support|tripod|support", oc):
                return True
            if category == "power" and re.search(r"batter|charger|power", oc):
                return True
            if category == "memory" and re.search(r"memory|storage", oc):
                return True
            return False

        return [p for p in self.products if keep(p)]

    def human_text(self, p):
        return _j(p, ["name", "brand", "model", "originalCategory", "category", "description", "keySpecifications", "specs", "compatibility", "useCases", "battery", "chargerPower"])

    def human_top(self, category, q, n=3):
        words = [w for w in re.split(r"\W+", q.lower()) if len(w) > 3]
        scored = []
        for p in self.human_catalogue(category):
            t = self.human_text(p)
            score = sum(2 for w in words if w in t)
            if p.get("sourceUrl") or p.get("specSource"):
                score += 1
            scored.append({"p": p, "score": score})
        scored.sort(key=lambda x: (-x["score"], x["p"]["name"]))
        return scored[:n]

    def human_list(self, title, items, closing=None):
        if not items:
            return None
        blocks = []
        for i, x in enumerate(items):
            p = x["p"]
            raw = p.get("keySpecifications") or p.get("specs") or p.get("description") or ""
            detail = " • ".join(raw.split("•")[:2]).strip()
            blocks.append(f"{i+1}. {p['name']}" + (f"\n   {detail}" if detail else ""))
        out = f"{title}\n\n" + "\n\n".join(blocks)
        if closing:
            out += f"\n\n{closing}"
        return out

    def human_answer(self, q):
        d = self.human_detect(q)
        st = self.state["human"]
        st["turns"] += 1
        if d["intent"]:
            st["lastIntent"] = d["intent"]
        if d["use"]:
            st["lastUse"] = d["use"]
        if d["intent"] in ("studio", "camera"):
            return None
        if d["intent"] == "lens":
            return self.human_list("Sure — here are a few lenses worth looking at:", self.human_top("lens", q),
                                    "Tell me which camera body you use and what you shoot most, and I’ll narrow this down properly.")
        if d["intent"] == "audio":
            title = "For a podcast setup, I’d look at these first:" if d["use"] == "podcast" else "For audio, these are good places to start:"
            return self.human_list(title, self.human_top("audio", q),
                                    "If you tell me how many people you need to record and whether you want wired or wireless, I can make this much more specific.")
        if d["intent"] == "lighting":
            return self.human_list("For lighting, I’d start here:", self.human_top("lighting", q),
                                    "Tell me the room size and whether this is for portraits, products, video or events, and I’ll help you build the rest.")
        if d["intent"] == "live-production":
            return self.human_list("For the live-production side, these are worth considering:", self.human_top("live-production", q),
                                    "How many cameras will you use, and are they feeding HDMI or SDI? That will decide the rest of the setup.")
        if d["intent"] == "support":
            return self.human_list("For support, I’d consider these:", self.human_top("support", q),
                                    "Tell me the camera and lens you’ll mount on it so I can avoid recommending something too light for the job.")
        if d["intent"] == "power":
            return self.human_list("I can help with power, but compatibility matters here. These are relevant catalogue options:", self.human_top("power", q),
                                    "Send me the exact camera model and I’ll match the battery/charger instead of guessing.")
        if d["intent"] == "memory":
            return self.human_list("For memory/storage, these are relevant options:", self.human_top("memory", q),
                                    "Tell me the exact camera or recorder and your recording format so I can check what speed/capacity makes sense.")
        if d["intent"] == "gimbal":
            return self.human_list("For stabilization, I’d look at these:", self.human_top("gimbal", q),
                                    "Tell me your camera and lens combination so we can choose based on the actual payload.")
        if d["intent"] == "printing":
            return self.human_list("For printing/photo work, these are relevant options:", self.human_top("printing", q),
                                    "Tell me the print size and typical monthly volume and I’ll narrow it down.")
        return None

    # ================================================================
    # EFIA_BROAD_V669  (app.js 1431-1478)
    # ================================================================
    def broad_txt(self, p):
        return _j(p, ["name", "brand", "model", "originalCategory", "category", "description", "keySpecifications", "specs", "compatibility", "useCases", "battery", "chargerPower"])

    def broad_norm(self, s):
        return re.sub(r"[^a-zA-Z0-9]+", " ", s or "").lower().strip()

    def broad_exact(self, q):
        nq = self.broad_norm(q)
        scored = []
        for p in self.products:
            name, model, brand = self.broad_norm(p.get("name")), self.broad_norm(p.get("model")), self.broad_norm(p.get("brand"))
            s = 0
            if name and name in nq:
                s += 30
            if model and len(model) > 2 and model in nq:
                s += 28
            if brand and brand in nq:
                s += 3
            toks = [t for t in (name + " " + model).split() if len(t) > 2]
            s += sum(2 for t in toks if t in nq)
            scored.append({"p": p, "score": s})
        scored = [x for x in scored if x["score"] >= 8]
        scored.sort(key=lambda x: -x["score"])
        return scored[0] if scored else None

    def broad_detect(self, q):
        s = q.lower()
        if re.search(r"\b(compare|versus|vs\.?|difference between)\b", s):
            return "compare"
        if re.search(r"\b(compatible|work with|fits?|battery for|charger for|lens for)\b", s):
            return "compatibility"
        if re.search(r"\b(spec|specification|tell me about|what is|details|features)\b", s):
            return "product-info"
        if re.search(r"\b(do you have|stock|carry|sell)\b", s):
            return "availability"
        return ""

    def broad_concise_product(self, p):
        raw = p.get("keySpecifications") or p.get("specs") or p.get("description") or ""
        bits = [x.strip() for x in re.split(r"[•\n]", raw) if x.strip()][:3]
        bits_txt = "\n" + "\n".join("• " + x for x in bits) if bits else ""
        return f"{p['name']}{bits_txt}"

    def broad_answer(self, q):
        st = self.state["broad"]
        st["turns"] += 1
        mode = self.broad_detect(q)
        hit = self.broad_exact(q)
        if not hit:
            return None
        p = hit["p"]
        st["lastProducts"] = [p["sku"]]
        st["lastIntent"] = mode or "product"
        if mode == "availability":
            return (f"Yes — {p['name']} is in the Adorias catalogue.\n\n{self.broad_concise_product(p)}\n\n"
                    "Want the key specs, compatible accessories, or help deciding whether it suits what you shoot?")
        if mode == "compatibility":
            c, b, ch = (p.get("compatibility") or "").strip(), (p.get("battery") or "").strip(), (p.get("chargerPower") or "").strip()
            facts = [f"Compatibility: {c}" if c else None, f"Battery: {b}" if b else None, f"Power/charger: {ch}" if ch else None]
            facts = [f for f in facts if f]
            if facts:
                return (f"{p['name']}\n\n" + "\n".join(facts) +
                        "\n\nIf you give me the exact other product you want to pair with it, I’ll check the relationship rather than assume it fits.")
            return (f"I found {p['name']}, but I don't have enough verified compatibility detail in the catalogue to "
                    "promise that pairing. Give me the exact product you want to connect it to and I’ll check what we know.")
        return f"{self.broad_concise_product(p)}\n\nTell me what you want to use it for and I can give you the practical pros, limitations and accessories that matter."

    # ================================================================
    # EFIA_BUDGET_V670  (app.js 1483-1569)
    # ================================================================
    def budget_extract(self, q):
        s = q.lower()
        m = (re.search(r"(?:budget(?:\s+(?:is|of))?|under|around|about|max(?:imum)?|spend)\D{0,12}(?:ghs|ghc|gh₵|₵)?\s*([\d,.]+)", s, re.I)
             or re.search(r"(?:ghs|ghc|gh₵|₵)\s*([\d,.]+)", s, re.I)
             or re.search(r"([\d,.]+)\s*(?:ghs|ghc|cedis?)", s, re.I))
        if not m:
            return None
        n = _num(m.group(1))
        return n if n and n > 0 else None

    def budget_text(self, p):
        return _j(p, ["name", "brand", "model"])

    def budget_benchmark(self, p):
        t = self.budget_text(p)
        b = next((x for x in BUDGET_BENCHMARKS if any(k in t for k in x["keys"])), None)
        if not b:
            return None
        direct = b["usd"] * BUDGET_FX["usdGhs"]
        return {**b, "directGhs": direct, "planningLow": direct * 1.10, "planningHigh": direct * 1.30}

    def budget_assess(self, p, budget):
        b = self.budget_benchmark(p)
        if not b:
            return {"status": "unknown", "b": None}
        if b["planningHigh"] <= budget:
            return {"status": "comfortably-within", "b": b}
        if b["planningLow"] <= budget:
            return {"status": "around-budget", "b": b}
        return {"status": "over", "b": b}

    def budget_camera_candidates(self, use):
        return self.dynamic_camera_rank({"intent": "camera", "use": use or "", "budget": None})

    def budget_answer(self, q):
        budget = self.budget_extract(q)
        if not budget:
            return None
        s = q.lower()
        use = ""
        if re.search(r"\b(wedding|bridal)\b", s):
            use = "wedding"
        elif re.search(r"\b(sport|football|soccer|action)\b", s):
            use = "sports"
        elif re.search(r"\b(wildlife|bird)\b", s):
            use = "wildlife"
        elif re.search(r"\b(portrait|headshot|family)\b", s):
            use = "portrait"
        elif re.search(r"\b(youtube|vlog|creator)\b", s):
            use = "creator"
        elif re.search(r"\b(event|birthday|graduation|ceremony)\b", s):
            use = "event"
        camera_intent = bool(re.search(r"\b(camera|photograph|photography|wedding|sport|wildlife|portrait|youtube|vlog|event)\b", s))
        if not camera_intent:
            return None

        ranked = self.budget_camera_candidates(use)
        known, unknown = [], []
        for x in ranked:
            a = self.budget_assess(x["p"], budget)
            (unknown if a["status"] == "unknown" else known).append({**x, **a})
        viable = [x for x in known if x["status"] != "over"][:3]
        near = sorted((x for x in known if x["status"] == "over"), key=lambda x: x["b"]["planningLow"])[:2]
        picks = viable or near
        if not picks:
            return (f"With a GHS {_fmt_money(budget)} budget, I can narrow the job down, but I don't have a "
                     "reliable external price benchmark for the suitable Adorias cameras yet. I’d rather not "
                     "pretend a model fits the budget. I can still recommend by capability, then confirm the "
                     "actual Adorias price with you.")

        lines = []
        for i, x in enumerate(picks):
            b = x["b"]
            range_txt = f"about GHS {_fmt_money(round(b['planningLow']/100)*100)}–{round(b['planningHigh']/100)*100}"
            fit = ("comfortably inside the planning budget" if x["status"] == "comfortably-within"
                   else "around your planning budget" if x["status"] == "around-budget"
                   else "likely above this budget new")
            lines.append(f"{i+1}. {x['p']['name']}\n   {fit}. External-market planning range: {range_txt}.")
        intro = (f"With about GHS {_fmt_money(budget)} to work with, these are the strongest budget-aware options I can currently benchmark:"
                  if viable else
                  f"At GHS {_fmt_money(budget)}, the suitable models I can price-benchmark are likely above budget new. The nearest are:")
        return (f"{intro}\n\n" + "\n\n".join(lines) +
                "\n\nThese are planning estimates, not Adorias prices. They use manufacturer US reference pricing "
                f"converted at USD 1 ≈ GHS {BUDGET_FX['usdGhs']:.2f}, with a 10–30% allowance for local/landed-market "
                "variation. Actual Ghana and Adorias prices can differ.")

    # ================================================================
    # EFIA_SCHOOL_V671  (app.js 1596-1619)
    # ================================================================
    def school_answer(self, q):
        s = q.lower()
        if not re.search(r"\bschool\b", s) or not re.search(r"\b(camera|photograph|photo|video|media)\b", s):
            return None
        specific = bool(re.search(r"\b(sport|football|event|graduation|classroom|youtube|video|photo|yearbook|media club|livestream)\b",
                                   re.sub(r"\bschool\b", "", s)))
        if specific:
            return None
        return (
            "A school can need a camera for very different jobs, so I wouldn't jump straight to one expensive full-frame body.\n\n"
            "1. General school photos & events\n"
            "A flexible photo/hybrid camera is usually the best starting point for assemblies, graduations, clubs and everyday documentation.\n\n"
            "2. Sports\n"
            "Prioritize autofocus, burst shooting and a suitable telephoto lens.\n\n"
            "3. Video / media club\n"
            "Prioritize reliable 4K video, easy audio connection, good autofocus and simple operation for students or staff.\n\n"
            "4. Livestreaming\n"
            "The camera is only one part — video output, power, tripod, capture/switching and audio matter too.\n\n"
            "Tell me which of those is closest, your approximate GHS budget, and whether students or staff will operate it. "
            "Then I can narrow the Adorias catalogue properly."
        )

    # ================================================================
    # EFIA_CLARIFY_V672  (app.js 1624-1765)
    # ================================================================
    CLARIFY_TOPICS = [
        ("livestream", r"\b(livestream|live stream|streaming|multicam|multi-camera)\b"),
        ("gimbal", r"\b(gimbal|stabili[sz]er|dji rs)\b"),
        ("lens", r"\b(lens|lenses|50mm|85mm|24-70|70-200|telephoto|wide angle)\b"),
        ("audio", r"\b(mics?|microphones?|podcast|audio recorder|wireless audio|voice ?over)\b"),
        ("lighting", r"\b(lights?|lighting|softbox(?:es)?|flash|strobe|led panel)\b"),
        ("support", r"\b(tripod|monopod|fluid head|camera support)\b"),
        ("power", r"\b(batter(?:y|ies)|charger|dummy battery|continuous power)\b"),
        ("memory", r"\b(memory card|sd cards?|storage|ssd|hard drive|card reader)\b"),
        ("printing", r"\b(printer|printing|photo paper|passport photos?)\b"),
        ("studio", r"\b(photo studio|photography studio|studio setup|build .*studio)\b"),
        ("camera", r"\b(camera|dslr|mirrorless|camcorder|photograph|photography)\b"),
    ]
    CLARIFY_USES = [
        ("school", r"\bschool\b"), ("wedding", r"\b(weddings?|bridal)\b"),
        ("sports", r"\b(sports?|football|soccer|basketball|action)\b"), ("wildlife", r"\b(wildlife|birds?)\b"),
        ("portrait", r"\b(portraits?|headshots?|family photos?)\b"), ("creator", r"\b(youtube|vlog|creator|tiktok)\b"),
        ("church", r"\b(church|worship|ministry)\b"), ("podcast", r"\bpodcast\b"), ("interview", r"\binterviews?\b"),
        ("event", r"\b(events?|birthdays?|baby showers?|graduations?|ceremon(?:y|ies))\b"),
        ("product", r"\bproduct (?:photo|photography|shoot)\b"),
    ]

    def clarify_extract(self, q):
        st = self.state["clarify"]
        s = q.lower()
        st["turns"] += 1

        for v, pat in self.CLARIFY_TOPICS:
            if re.search(pat, s):
                st["topic"] = v
                break
        for v, pat in self.CLARIFY_USES:
            if re.search(pat, s):
                st["use"] = v
                break

        model_hint = re.search(
            r"\b(?:my|on my|for my|with my|on|for|with)\s+((?:canon|nikon|sony|panasonic|blackmagic|dji)\s+[a-z0-9][a-z0-9 .\-]{1,45}?)(?=\s+(?:with|and|using|for|lens|body)\b|$)",
            s, re.I)
        if model_hint:
            st["camera"] = model_hint.group(1).strip()
            st["answered"]["camera"] = True

        people_words = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6}
        pm = re.search(r"\b(one|two|three|four|five|six)[ -](?:person|people|speaker|presenter)", s, re.I)
        if pm:
            st["people"] = people_words[pm.group(1).lower()]
            st["answered"]["people"] = True

        m = (re.search(r"(?:budget(?:\s+(?:is|of))?|under|around|about|max(?:imum)?|spend)\D{0,12}(?:ghs|ghc|₵)?\s*([\d,.]+)", s, re.I)
             or re.search(r"(?:ghs|ghc|₵)\s*([\d,.]+)", s, re.I))
        if m:
            st["budget"] = _num(m.group(1))
            st["answered"]["budget"] = True
        if re.search(r"\b(no fixed budget|budget flexible|flexible budget)\b", s):
            st["answered"]["budget"] = True

        m = re.search(r"\b(\d+)\s*(?:people|persons|speakers|presenters|guests)\b", s)
        if m:
            st["people"] = int(m.group(1))
            st["answered"]["people"] = True
        m = re.search(r"\b(\d+)\s*cameras?\b", s)
        if m:
            st["cameras"] = int(m.group(1))
            st["answered"]["cameras"] = True
        if re.search(r"\b(hdmi|sdi|usb)\b", s):
            st["outputs"] = "/".join(re.findall(r"\b(hdmi|sdi|usb)\b", s)).upper()
            st["answered"]["outputs"] = True
        if re.search(r"\b(students?|staff|teachers?|volunteers?|professional operator|camera operator)\b", s):
            om = re.search(r"\b(students?|staff|teachers?|volunteers?|professional operator|camera operator)\b", s)
            st["operator"] = om.group(0) if om else ""
            st["answered"]["operator"] = True
        m = re.search(r"\b(?:room|space|studio)\s*(?:is|about|around)?\s*(\d+(?:\.\d+)?)\s*(?:x|by)\s*(\d+(?:\.\d+)?)\s*(m|metres?|meters?|ft|feet)?", s, re.I)
        if m:
            st["room"] = f"{m.group(1)} × {m.group(2)} {m.group(3) or ''}".strip()
            st["answered"]["room"] = True
        rm = re.search(r"\b(small|medium|large)\s+(?:room|studio|space)\b", s)
        if rm:
            st["room"] = rm.group(0)
            st["answered"]["room"] = True

        own = re.search(r"(?:already have|already own|i have|we have)\s+([^.!?]+)", s, re.I)
        if own:
            st["existing"].append(own.group(1).strip())
            st["answered"]["existing"] = True
        if re.search(r"\b(starting from scratch|own nothing|have nothing)\b", s):
            st["answered"]["existing"] = True

        last = st["asked"][-1] if st["asked"] else None
        if last == "use" and len(q.strip()) < 120:
            st["use"] = st["use"] or q.strip()
            st["answered"]["use"] = True
        if last == "camera" and len(q.strip()) < 120:
            st["camera"] = q.strip()
            st["answered"]["camera"] = True
        if last == "budget" and not st["answered"].get("budget") and re.search(r"\d", s):
            n = re.search(r"[\d,]+", s)
            if n:
                st["budget"] = _num(n.group(0))
                st["answered"]["budget"] = True
        if last == "people" and not st["answered"].get("people") and re.search(r"\d", s):
            n = re.search(r"\d+", s)
            if n:
                st["people"] = int(n.group(0))
                st["answered"]["people"] = True
        if last == "cameras" and not st["answered"].get("cameras") and re.search(r"\d", s):
            n = re.search(r"\d+", s)
            if n:
                st["cameras"] = int(n.group(0))
                st["answered"]["cameras"] = True
        if last == "operator" and len(q.strip()) < 80:
            st["operator"] = q.strip()
            st["answered"]["operator"] = True
        if last == "room" and len(q.strip()) < 80:
            st["room"] = q.strip()
            st["answered"]["room"] = True
        if last == "outputs" and re.search(r"\b(hdmi|sdi|usb)\b", s):
            st["outputs"] = "/".join(re.findall(r"\b(hdmi|sdi|usb)\b", s)).upper()
            st["answered"]["outputs"] = True
        return st

    def clarify_mark(self, key):
        st = self.state["clarify"]
        if key not in st["asked"]:
            st["asked"].append(key)
        return key

    def clarify_question(self):
        st = self.state["clarify"]
        t = st["topic"]
        answered = st["answered"]
        if t == "camera":
            if not st["use"]:
                return self._ca(self.clarify_mark("use"), "What will you mainly use the camera for — photos, video, sports, events, livestreaming, or a mixture?")
            if st["use"] == "school" and not answered.get("operator"):
                return self._ca(self.clarify_mark("operator"), "For the school, will it mainly be used by students, staff, or an experienced camera operator?")
            if not answered.get("budget"):
                return self._ca(self.clarify_mark("budget"), "Roughly what GHS budget would you like me to work within?")
        if t == "lens":
            if not st["camera"] and not answered.get("camera"):
                return self._ca(self.clarify_mark("camera"), "Which exact camera body will you use the lens on? That lets me match the mount instead of guessing.")
            if not st["use"]:
                return self._ca(self.clarify_mark("use"), "What will you mainly shoot with it — portraits, weddings, sports, wildlife, video, products, or something else?")
        if t == "audio":
            if not st["use"]:
                return self._ca(self.clarify_mark("use"), "What are you recording — interviews, a podcast, church, events, YouTube, or something else?")
            if not answered.get("people"):
                return self._ca(self.clarify_mark("people"), "How many people do you need to record at the same time?")
        if t == "lighting":
            if not st["use"]:
                return self._ca(self.clarify_mark("use"), "What will you light most often — portraits, products, video, events, or a studio space?")
            if not answered.get("room") and not re.search(r"\bevent|location|outdoor\b", str(st["use"]), re.I):
                return self._ca(self.clarify_mark("room"), "Roughly how large is the room or shooting space?")
        if t == "support":
            if not st["camera"] and not answered.get("camera"):
                return self._ca(self.clarify_mark("camera"), "What camera and lens will the tripod/support carry? I want to size it for the actual load.")
            if not st["use"]:
                return self._ca(self.clarify_mark("use"), "Is this mainly for photography, video, sports, livestreaming, or travel?")
        if t == "power":
            if not st["camera"] and not answered.get("camera"):
                return self._ca(self.clarify_mark("camera"), "What is the exact camera/device model? Battery and charger compatibility is model-specific.")
        if t == "memory":
            if not st["camera"] and not answered.get("camera"):
                return self._ca(self.clarify_mark("camera"), "What exact camera or recorder is the memory for?")
            if not st["use"]:
                return self._ca(self.clarify_mark("use"), "Will you mainly shoot photos, 4K video, long events, or something else?")
        if t == "gimbal":
            if not st["camera"] and not answered.get("camera"):
                return self._ca(self.clarify_mark("camera"), "What camera and lens combination will you put on the gimbal? Payload matters here.")
        if t == "printing":
            if not st["use"]:
                return self._ca(self.clarify_mark("use"), "What are you mainly printing — passport photos, customer photo prints, albums, or something else?")
        if t == "livestream":
            if not answered.get("cameras"):
                return self._ca(self.clarify_mark("cameras"), "How many cameras do you want in the livestream?")
            if not answered.get("outputs"):
                return self._ca(self.clarify_mark("outputs"), "Do the cameras output HDMI or SDI, if you know? If you're not sure, send me the camera models.")
            if not answered.get("budget"):
                return self._ca(self.clarify_mark("budget"), "What approximate GHS budget should I build the livestream around?")
        if t == "studio":
            if not st["use"]:
                return self._ca(self.clarify_mark("use"), "What will you shoot most in the studio — portraits, products, babies/families, fashion, video, or a mixture?")
            if not answered.get("room"):
                return self._ca(self.clarify_mark("room"), "Roughly how large is the shooting space?")
            if not answered.get("existing"):
                return self._ca(self.clarify_mark("existing"), "What gear do you already own? You can also say “starting from scratch.”")
            if not answered.get("budget"):
                return self._ca(self.clarify_mark("budget"), "What approximate GHS budget would you like the complete studio to stay within?")
        return ""

    @staticmethod
    def _ca(_key, text):
        return text

    def clarify_answer(self, q):
        st = self.clarify_extract(q)
        if not st["topic"]:
            return None
        ask = self.clarify_question()
        if not ask:
            return None
        lead = "Sure. " if st["turns"] == 1 else ""
        return lead + ask

    # ================================================================
    # EFIA_MULTI_V673  (app.js 1770-1895)
    # ================================================================
    def multi_detect(self, q):
        need = re.sub(
            r"\b(?:already have|already own|using|for my|on my|with my)\b[^,;.]*?(?=\b(?:but|and i need|and we need)\b|[,;.]|$)",
            "", q, flags=re.I)
        keys = [k for k, d in MULTI_DEFINITIONS.items() if d[1].search(need)]
        if re.search(r"\bcamera\s+(?:bag|battery|charger|strap|lens|tripod|support|mount|adapter)\b", need, re.I) and \
           not re.search(r"\bcamera\s*(?:and|&|,|plus)\b", need, re.I):
            return [k for k in keys if k != "camera"]
        return keys

    def multi_explain(self):
        st = self.state["multi"]["active"]
        prompts = {
            "use": "Will you take photos, record videos, or do both? For example, photos of people or products, or videos for YouTube.",
            "budget": "How much would you like to spend on everything together? You can say “GHS 10,000”, give another currency, or say “not sure yet”.",
            "room": "Is the space about the size of a small bedroom, a classroom, or a large hall? A rough description is enough.",
            "people": "How many people need microphones at the same time? For example, one presenter or two people talking.",
            "existing": "What equipment do you already have that you want to keep using? If you have none, say “starting from scratch”.",
        }
        return f"No problem. {prompts.get(st['pending']) or st['lastQuestion']}"

    def multi_plan(self):
        st = self.state["multi"]["active"]
        photo_only = bool(re.search(r"photo|portrait", st["use"], re.I)) and not re.search(r"video|both", st["use"], re.I)
        brief = {
            "camera": "A camera and suitable lens, with budget left for the other equipment.",
            "lens": "A lens that fits your camera and shooting space.",
            "lighting": "One light, a softbox and a stable stand." if photo_only else "One continuous light, a softbox and a stable stand for photos and video.",
            "audio": "Microphones for your speakers, with connections matched to your recording device.",
            "support": "A tripod rated for your camera and lens.",
            "gimbal": "A gimbal that can balance your camera and lens.",
            "power": "Batteries or continuous power matched to each device.",
            "memory": "Memory cards matched to your camera and recording mode.",
            "production": "Compatible camera outputs, switching, audio and streaming equipment.",
            "cables": "Cables with the right connectors, signal format and length.",
            "backgrounds": "A background and secure support sized for your room.",
            "printing": "A printer and paper suited to your print size and volume.",
        }
        blocks = [f"{i+1}. {MULTI_DEFINITIONS[k][0]}\n{brief[k]}" for i, k in enumerate(st["categories"])]
        return f"Here’s a starting setup:\n\n" + "\n\n".join(blocks) + f"\n\nTotal budget: {st['budget']}. Prices and compatibility need confirmation.\n\nWhich part shall we choose first?"

    def multi_answer(self, q):
        mstate = self.state["multi"]

        if re.search(r"\b(start over|new request|new topic|forget (?:that|the setup)|reset)\b", q, re.I):
            mstate["active"] = None
            mstate["seed"] = []
            self.state["clarify"] = default_state()["clarify"]
            self.state["project"] = default_state()["project"]
            self.state["dynamic"] = default_state()["dynamic"]
            return "Let’s start fresh. What equipment do you need, and what will you use it for?"

        found = self.multi_detect(q)
        if not mstate["active"]:
            if re.search(r"\b(also|add|as well|plus|too)\b", q, re.I):
                found = list(dict.fromkeys((mstate.get("seed") or []) + found))
            if len(found) < 2:
                if found:
                    mstate["seed"] = found
                return None
            mstate["active"] = {"categories": found, "use": "", "budget": "", "room": "", "people": "",
                                 "existing": "", "pending": "", "lastQuestion": "", "ready": False}

        st = mstate["active"]
        if re.search(r"\b(don[’']?t understand|do not understand|confused|what do you mean|explain (?:that|the question)|simpler)\b", q, re.I):
            return self.multi_explain()
        if re.search(r"\b(remove|drop|skip|without|don[’']?t need|do not need)\b", q, re.I):
            st["categories"] = [k for k in st["categories"] if k not in found]
            if not st["categories"]:
                mstate["active"] = None
                mstate["seed"] = []
                return "What would you like help choosing instead?"
        else:
            for k in found:
                if k not in st["categories"]:
                    st["categories"].append(k)

        pending = st["pending"]
        budget = re.search(r"(?:GHS|GHC|₵|USD|\$|GBP|£|EUR|€)\s*[\d,]+(?:\.\d+)?(?:\s*[kK]\b)?", q, re.I)
        if budget:
            st["budget"] = re.sub(r",+$", "", budget.group(0))
        room = re.search(r"\b(?:small|medium|large)\s+(?:studio(?:\s+space)?|room|space|hall)|\b\d+(?:\.\d+)?\s*(?:x|by)\s*\d+(?:\.\d+)?\s*(?:m|metres?|meters?|ft|feet)\b", q, re.I)
        if room:
            st["room"] = room.group(0)
        use = re.search(r"\b(?:portraits?|headshots?|product (?:photos?|photography)|weddings?|school|church|podcast|interviews?|youtube|photos? and videos?|photography|videos?|photos?|sports?)\b", q, re.I)
        if use:
            st["use"] = use.group(0)
        own = re.search(r"\b(?:already have|already own|i have|we have)\s+(.+?)(?=\b(?:but|and i need)\b|$)", q, re.I)
        if own:
            st["existing"] = own.group(1).strip()
        if re.search(r"\b(starting from scratch|nothing|none)\b", q, re.I):
            st["existing"] = "starting from scratch"
        people = re.search(r"\b(\d+|one|two|three|four|five|six)[ -]*(?:people|persons?|speakers?|presenters?|guests?)\b", q, re.I)
        if people:
            st["people"] = people.group(1)

        if pending and not re.search(r"\?$", q.strip()) and not re.search(r"\b(add|remove|drop|also need)\b", q, re.I):
            if pending == "budget" and not st["budget"] and re.search(r"\d|not sure|flexible|don[’']?t know", q, re.I):
                st["budget"] = q.strip()
            elif pending == "use" and not st["use"]:
                st["use"] = q.strip()
            elif pending in ("room", "people", "existing") and not st[pending]:
                st[pending] = q.strip()
        st["pending"] = ""

        if not st["use"]:
            st["pending"] = "use"
            st["lastQuestion"] = "Will you use the setup for photos, videos, or both?"
            return st["lastQuestion"]
        if not st["budget"]:
            st["pending"] = "budget"
            st["lastQuestion"] = "What’s your total budget, and in which currency?"
            return st["lastQuestion"]
        if "lighting" in st["categories"] and not st["room"]:
            st["pending"] = "room"
            st["lastQuestion"] = "Is your space small, medium or large?"
            return st["lastQuestion"]
        if "audio" in st["categories"] and not st["people"]:
            st["pending"] = "people"
            st["lastQuestion"] = "How many people need microphones at once?"
            return st["lastQuestion"]
        if not st["existing"]:
            st["pending"] = "existing"
            st["lastQuestion"] = "Do you already have any equipment, or are you starting from scratch?"
            return st["lastQuestion"]

        was_ready = st["ready"]
        st["ready"] = True
        exact = self.find_product(q)
        if exact and re.search(r"\b(specs?|details?|tell me|compatible|work with|what about)\b", q, re.I):
            spec = exact.get("keySpecifications") or exact.get("specs") or exact.get("description") or "Exact specifications need confirmation."
            return f"{exact['name']}\n{spec}\n\nCompatibility with your other equipment needs confirmation."

        if was_ready and len(found) == 1 and not re.search(r"\b(add|remove|drop|skip|without)\b", q, re.I):
            k = found[0]
            d = MULTI_DEFINITIONS[k]
            pool = [p for p in self.products if p.get("originalCategory") in d[2]]
            if k == "memory":
                pool = [p for p in pool if re.search(r"memory|sd card|ssd|storage", (p.get("name") or "") + " " + (p.get("description") or ""), re.I)]
            if k == "gimbal":
                pool = [p for p in pool if re.search(r"gimbal|stabili[sz]er", (p.get("name") or "") + " " + (p.get("description") or ""), re.I)]
            tokens = [t for t in re.split(r"\W+", st["use"].lower()) if len(t) > 3]

            def score(p):
                blob = " ".join(x for x in [p.get("description"), p.get("useCases"), p.get("compatibility")] if x).lower()
                return sum(1 for t in tokens if t in blob)

            pool.sort(key=lambda p: -score(p))
            choices = []
            for i, p in enumerate(pool[:3]):
                spec = p.get("keySpecifications") or p.get("specs") or p.get("description") or "Exact specifications need confirmation."
                facts = [f for f in re.split(r"\s*[•;]\s*", spec) if f]
                selected = facts[:3]
                video = next((t for t in facts if re.search(r"4k|8k|full hd|video", t, re.I)), None)
                if k == "camera" and re.search(r"both|video", st["use"], re.I) and video and video not in selected:
                    if len(selected) > 2:
                        selected[2] = video
                    else:
                        selected.append(video)
                details = "\n".join("• " + t for t in selected)
                choices.append(f"{i+1}. {p['name']}\n{details}")
            body = ("Three catalogue options to compare:\n\n" + "\n\n".join(choices)) if choices else "I need to confirm a suitable catalogue item."
            return f"{body}\n\nPrices and fit within your {st['budget']} total budget need confirmation.\n\nWhich option interests you?"

        return self.multi_plan()
