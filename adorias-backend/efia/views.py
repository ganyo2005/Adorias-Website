from rest_framework.views import APIView
from rest_framework.response import Response

from catalogue.utils import all_products_as_dicts
from .engine import EfiaEngine, default_state

FALLBACK = ("I can help with Adorias equipment, but I don't want to guess. Tell me the exact product or "
            "camera model and what you want to use it for.")


class EfiaChatView(APIView):
    def post(self, request):
        message = (request.data.get("message") or "").strip()
        if not message:
            return Response({"reply": FALLBACK})

        state = request.session.get("efia_state") or default_state()
        # New keys added after a session was created still get sane defaults.
        for key, value in default_state().items():
            state.setdefault(key, value)

        engine = EfiaEngine(state, all_products_as_dicts())
        reply = engine.answer(message) or FALLBACK

        request.session["efia_state"] = engine.state
        request.session.modified = True
        return Response({"reply": reply})
