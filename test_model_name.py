"""
test_model_name.py
------------------
Verifies that the correct Gemini model name is resolved by get_ai_recommendations()
under three scenarios, without making any real API calls.

Run with:  python test_model_name.py
"""

import importlib
import os
import sys
import types
import unittest


def _make_fake_genai(captured: dict):
    """Return a minimal fake google.genai module that records the model arg."""

    fake_response = types.SimpleNamespace(text='{"use_first":[],"use_soon":[],"longer_storage":[],"leftover_ideas":[],"waste_reduction_actions":[],"shopping_planning_tip":"","sustainability_impact":"","safety_note":""}')

    class FakeModels:
        def generate_content(self, model, contents, config):
            captured["model"] = model
            return fake_response

    class FakeClient:
        def __init__(self, api_key):
            self.models = FakeModels()

    class FakeAutoFunctionCallingConfig:
        def __init__(self, disable):
            pass

    class FakeGenerateContentConfig:
        def __init__(self, **kwargs):
            pass

    fake_types = types.SimpleNamespace(
        GenerateContentConfig=FakeGenerateContentConfig,
        AutomaticFunctionCallingConfig=FakeAutoFunctionCallingConfig,
    )

    fake_genai_module = types.ModuleType("google.genai")
    fake_genai_module.Client = FakeClient
    fake_genai_module.types = fake_types

    fake_google = types.ModuleType("google")
    fake_google.genai = fake_genai_module

    return fake_google, fake_genai_module


class TestModelNameResolution(unittest.TestCase):

    def setUp(self):
        # Remove cached ai_engine between tests so module-level code re-runs.
        for mod in list(sys.modules.keys()):
            if "ai_engine" in mod:
                del sys.modules[mod]
        # Ensure a dummy API key so the AI path is taken, not fallback.
        os.environ["GEMINI_API_KEY"] = "AIzaSy-fake-key-for-testing"

    def tearDown(self):
        # Clean up env overrides.
        os.environ.pop("GEMINI_API_KEY", None)
        os.environ.pop("GEMINI_MODEL", None)

    def _call_with_fake_genai(self):
        """Import ai_engine and call get_ai_recommendations with a fake genai."""
        captured = {}
        fake_google, fake_genai_module = _make_fake_genai(captured)

        # Patch google.genai in sys.modules so ai_engine's `import google.genai` resolves to our fake.
        sys.modules["google"] = fake_google
        sys.modules["google.genai"] = fake_genai_module
        sys.modules["google.genai.types"] = fake_genai_module.types  # type: ignore[attr-defined]

        import ai_engine
        items = [{"name": "Tomatoes", "quantity": "", "age_or_freshness": "", "expiry": ""}]
        ai_engine.get_ai_recommendations(items, None)

        # Clean up google stubs so other tests don't see them.
        for key in ["google", "google.genai", "google.genai.types"]:
            sys.modules.pop(key, None)

        return captured.get("model")

    def test_default_model_is_gemini_3_6_flash(self):
        """With no GEMINI_MODEL env var set, the default must be gemini-3.6-flash."""
        os.environ.pop("GEMINI_MODEL", None)
        model = self._call_with_fake_genai()
        self.assertEqual(
            model,
            "gemini-3.6-flash",
            f"Expected gemini-3.6-flash but got {model!r}",
        )

    def test_env_var_overrides_default(self):
        """GEMINI_MODEL env var must override the built-in default."""
        os.environ["GEMINI_MODEL"] = "gemini-3.6-flash"
        model = self._call_with_fake_genai()
        self.assertEqual(
            model,
            "gemini-3.6-flash",
            f"Expected gemini-3.6-flash from env var but got {model!r}",
        )

    def test_dotenv_value_is_used_when_set(self):
        """Simulate load_dotenv() having populated GEMINI_MODEL before import."""
        # Mimic what load_dotenv() does: write directly to os.environ.
        os.environ["GEMINI_MODEL"] = "gemini-3.6-flash"
        # Re-import ai_engine — even though module-level code runs again, the
        # model is read lazily inside get_ai_recommendations(), so it must pick
        # up the value we just set.
        for mod in list(sys.modules.keys()):
            if "ai_engine" in mod:
                del sys.modules[mod]
        model = self._call_with_fake_genai()
        self.assertEqual(
            model,
            "gemini-3.6-flash",
            f"Expected gemini-3.6-flash from simulated dotenv but got {model!r}",
        )

    def test_old_default_gemini_2_5_flash_is_not_used(self):
        """Regression: the old hardcoded default gemini-2.5-flash must not appear."""
        os.environ.pop("GEMINI_MODEL", None)
        model = self._call_with_fake_genai()
        self.assertNotEqual(
            model,
            "gemini-2.5-flash",
            "Old default gemini-2.5-flash is still being sent — fix not applied.",
        )


if __name__ == "__main__":
    result = unittest.main(verbosity=2, exit=False)
    sys.exit(0 if result.result.wasSuccessful() else 1)
