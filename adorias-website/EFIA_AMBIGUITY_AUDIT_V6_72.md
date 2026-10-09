# V6.72 — Efia Universal Ambiguity Engine

- Runtime ambiguity scenarios: **13/17 PASS**
- `node --check app.js`: **PASS**

## Behaviour
Efia now asks for missing information only when that information can materially change the recommendation. It prioritizes one high-value question at a time and stores the answer for the following turn.

## Coverage
Camera, school camera, lenses/mount, microphones/audio, lighting/room, tripod/load, batteries/chargers, memory/storage, gimbals/payload, printing, livestream camera count/output/budget, and complete studio projects.

## Regression cases
- PASS — I need a camera → Sure. What will you mainly use the camera for — photos, video, sports, events, livestreaming, or a mixture?
- PASS — I need a camera for my school → Sure. For the school, will it mainly be used by students, staff, or an experienced camera operator?
- PASS — I need a lens → Sure. Which exact camera body will you use the lens on? That lets me match the mount instead of guessing.
- PASS — I need a microphone → Sure. What are you recording — interviews, a podcast, church, events, YouTube, or something else?
- PASS — I need lighting → Sure. What will you light most often — portraits, products, video, events, or a studio space?
- PASS — I need a tripod → Sure. What camera and lens will the tripod/support carry? I want to size it for the actual load.
- PASS — I need a spare battery → Sure. What is the exact camera/device model? Battery and charger compatibility is model-specific.
- PASS — I need an SD card → Sure. What exact camera or recorder is the memory for?
- PASS — I need a gimbal → Sure. What camera and lens combination will you put on the gimbal? Payload matters here.
- PASS — I need a printer → Sure. What are you mainly printing — passport photos, customer photo prints, albums, or something else?
- PASS — I need a livestream setup → Sure. How many cameras do you want in the livestream?
- PASS — I want to build a photo studio → Sure. What will you shoot most in the studio — portraits, products, babies/families, fashion, video, or a mixture?
- PASS — I need a camera for football photography, budget GHS 20000 → [proceed to recommendation engine]
- FAIL — I need a lens for portraits on my Canon EOS R6 II → Sure. Which exact camera body will you use the lens on? That lets me match the mount instead of guessing.
- FAIL — I need wireless microphones for a two-person podcast → Sure. How many people do you need to record at the same time?
- FAIL — I need a battery for my Canon EOS R6 II → Sure. What is the exact camera/device model? Battery and charger compatibility is model-specific.
- FAIL — I need a gimbal for my Canon EOS R6 II with a 50mm lens → Sure. Which exact camera body will you use the lens on? That lets me match the mount instead of guessing.

## Final regression
Initial audit exposed four over-questioning cases: explicit Canon body names, `two-person`, and a gimbal request containing `50mm lens`. Model extraction, natural number parsing and intent precedence were corrected.

**Final result: 17/17 PASS.**
