"""Regression tests porting the original tests/efia-multi.cjs (14 scenarios)
and the tests/efia-readability.cjs transcript scenario from the JS site, to
verify the Python engine behaves identically to the original JavaScript.
Run with: python3 manage.py test efia
"""
import re

from django.core.management import call_command
from django.test import TestCase

from catalogue.utils import all_products_as_dicts
from .engine import EfiaEngine, default_state


def new_engine(products=None):
    return EfiaEngine(default_state(), products or [])


class MultiCategoryTests(TestCase):
    """Port of tests/efia-multi.cjs."""

    def test_camera_and_lighting_retained_plain_clarification(self):
        e = new_engine()
        r = e.multi_answer("I need a camera and light set up for my small studio space")
        st = e.state["multi"]["active"]
        self.assertEqual(st["categories"], ["camera", "lighting"])
        self.assertRegex(r, r"photos.*videos")
        self.assertEqual(st["room"], "small studio space")

    def test_confusion_does_not_become_a_use_case(self):
        e = new_engine()
        e.multi_answer("I need a camera and light set up for my small studio space")
        r = e.multi_answer("I DONT UNDERSTAND THIS QUESTION")
        st = e.state["multi"]["active"]
        self.assertRegex(r, r"photos of people or products")
        self.assertEqual(st["use"], "")
        self.assertEqual(st["pending"], "use")

    def test_whole_setup_budget_and_turn_memory(self):
        e = new_engine()
        e.multi_answer("I need a camera and lights for a small studio")
        e.multi_answer("both")
        r1 = e.multi_answer("GHS 15000")
        self.assertRegex(r1, r"already have")
        r = e.multi_answer("starting from scratch")
        self.assertRegex(r, r"1\. Camera")
        self.assertRegex(r, r"2\. Lighting")
        self.assertIn("GHS 15000", r)
        self.assertEqual(len(e.state["multi"]["active"]["categories"]), 2)

    def test_three_categories_answered_together(self):
        e = new_engine()
        r = e.multi_answer(
            "I need a camera, lights and microphones for videos in a small room, "
            "GHS 20000, two people, starting from scratch")
        for x in ["Camera", "Lighting", "Audio"]:
            self.assertIn(x, r)

    def test_separate_support_power_storage_categories(self):
        e = new_engine()
        e.multi_answer("I need a tripod, batteries and SD cards")
        self.assertEqual(len(e.state["multi"]["active"]["categories"]), 3)

    def test_printing_and_backgrounds(self):
        e = new_engine()
        e.multi_answer("I need a printer and backdrops")
        self.assertEqual(len(e.state["multi"]["active"]["categories"]), 2)

    def test_add_a_category_on_a_later_turn(self):
        e = new_engine()
        e.multi_answer("I need a camera and lights")
        e.multi_answer("also add a microphone")
        self.assertIn("audio", e.state["multi"]["active"]["categories"])

    def test_remove_one_category(self):
        e = new_engine()
        e.multi_answer("I need a camera and lights")
        e.multi_answer("remove lighting")
        self.assertEqual(e.state["multi"]["active"]["categories"], ["camera"])

    def test_reset_conversation(self):
        e = new_engine()
        e.multi_answer("camera and lighting")
        e.multi_answer("start over")
        self.assertIsNone(e.state["multi"]["active"])

    def test_standalone_remains_with_previous_engine(self):
        e = new_engine()
        self.assertIsNone(e.multi_answer("I need lighting"))

    def test_accessory_camera_mention_is_not_a_body_request(self):
        e = new_engine()
        self.assertIsNone(e.multi_answer("I need a camera battery"))
        self.assertIsNone(e.multi_answer("I need a lens for my Canon camera"))

    def test_build_request_across_successive_messages(self):
        e = new_engine()
        e.multi_answer("I need a camera")
        e.multi_answer("also lights")
        self.assertEqual(e.state["multi"]["active"]["categories"], ["camera", "lighting"])

    def test_currency_kept_explicit(self):
        e = new_engine()
        e.multi_answer("camera and lights for video in a small room, USD 2000, starting from scratch")
        self.assertEqual(e.state["multi"]["active"]["budget"], "USD 2000")

    def test_upstream_routing_precedes_single_category_clarification(self):
        import inspect
        src = inspect.getsource(EfiaEngine.answer)
        self.assertLess(src.index("multi_answer"), src.index("clarify_answer"))


class ReadabilityTranscriptTests(TestCase):
    """Port of the transcript scenario in tests/efia-readability.cjs, run
    against the real imported catalogue."""

    @classmethod
    def setUpTestData(cls):
        call_command("import_catalogue")

    def test_studio_setup_transcript(self):
        products = all_products_as_dicts()
        e = new_engine(products)
        turns = ["HELP ME SET UP MY STUDIO WITH A GOOD CAMERA AND LIGHT", "BOTH", "50000GHS",
                 "ITS A SMALL STUDIO", "NOTHING IM A BEGINNER", "CAMERA"]
        transcript = [e.multi_answer(q) for q in turns]

        for reply in transcript[:4]:
            self.assertLess(len(reply.split()), 17, reply)

        self.assertEqual(e.state["multi"]["active"]["existing"], "starting from scratch")
        self.assertNotIn("I'm planning", " ".join(transcript))
        self.assertLess(len(transcript[4].split()), 90)
        self.assertLess(len(transcript[5].split()), 125)
        self.assertIn("Canon", transcript[5])
        self.assertEqual(transcript[5].count("\n1."), 1)
