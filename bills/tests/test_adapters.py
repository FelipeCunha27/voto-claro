from django.test import TestCase
from bills.adapters.openai_adapter import generate_accessible_version, TransientGenerationError, PermanentGenerationError, GenerationResult
import openai

class MockOpenAIResponse:
    def __init__(self, parsed=None):
        self.parsed = parsed

class OpenAIAdapterTest(TestCase):
    def setUp(self):
        self.valid_response = GenerationResult(
            summary="A summary",
            who_is_affected="People",
            practical_changes="Changes",
            points_of_attention="Points",
            is_legislative_text=True,
            suggested_theme="Health"
        )
        
    def test_valid_generation(self):
        # We will mock the openai client inside the adapter, or we mock the adapter directly?
        # Better to mock the client parse method.
        import bills.adapters.openai_adapter as adapter_module
        
        class FakeClient:
            class beta:
                class chat:
                    class completions:
                        @staticmethod
                        def parse(*args, **kwargs):
                            return MockOpenAIResponse(parsed=GenerationResult(
                                summary="S", who_is_affected="W", practical_changes="P", points_of_attention="A", is_legislative_text=True, suggested_theme="T"
                            ))
                            
        original_client = adapter_module.client
        adapter_module.client = FakeClient
        try:
            res = generate_accessible_version("Texto", ["T"])
            self.assertEqual(res.summary, "S")
        finally:
            adapter_module.client = original_client
