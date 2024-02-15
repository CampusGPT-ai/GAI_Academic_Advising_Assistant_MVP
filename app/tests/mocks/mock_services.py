from ...cloud_services import openai_response_objects
from ...cloud_services.azure_cog_service import VectorSearchService
from ...cloud_services.llm_services import AILLMClients


class MockLLMClient:
    def __init__(self, *args, **kwargs):
        pass


class MockSearchClient:
    def __init__(self, *args, **kwargs):
        pass


class MockAzureLLMClients(AILLMClients):
    def __init__(self, *args, **kwargs):
        self.client = MockLLMClient()

    def stream(self, messages):
        pass

    def chat(self, messages, json_mode=False):
        return openai_response_objects.ChatCompletion(
            **{
                "id": "chatcmpl-8pnYQYs3zEyvYWNWWf6Ni18WVanEf",
                "object": "chat.completion",
                "created": 1707355906,
                "model": "gpt-35-turbo",
                "prompt_filter_results": [
                    {
                        "prompt_index": 0,
                        "content_filter_results": {
                            "hate": {"filtered": False, "severity": "safe"},
                            "self_harm": {"filtered": False, "severity": "safe"},
                            "sexual": {"filtered": False, "severity": "safe"},
                            "violence": {"filtered": False, "severity": "safe"},
                        },
                    }
                ],
                "choices": [
                    {
                        "finish_reason": "stop",
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": """
                                What are the Undergraduate Application Deadlines?
                                What is student life like on campus?
                                """,
                        },
                        "content_filter_results": {
                            "hate": {"filtered": False, "severity": "safe"},
                            "self_harm": {"filtered": False, "severity": "safe"},
                            "sexual": {"filtered": False, "severity": "safe"},
                            "violence": {"filtered": False, "severity": "safe"},
                        },
                    }
                ],
                "usage": {
                    "prompt_tokens": 458,
                    "completion_tokens": 69,
                    "total_tokens": 527,
                },
            }
        )

    def embed(self, text):
        pass

    def embed_many(self, inputs):
        pass

    def embed_to_array(self, text):
        pass


class MockAzureSearchService(VectorSearchService):
    def __init__(self, *args, **kwargs):
        self.llm_client = MockLLMClient()
        self.azure_search_client = MockSearchClient()

    def getSearchClient(self):
        return self.azure_search_client

    def simple_search(self, text, vector_field, n=3):
        return [
            {
                "content": """
                    What are the Undergraduate Application Deadlines?
                    What is student life like on campus?
                    """,
                "followups": """
                    Who can students contact for advising or academic issues?
                    What are the Policy for transfer credits?
                    """,
                "questions": """
                    Question: What are the Undergraduate Application Deadlines? \n Answer: For
                    freshers, the deadlines are May 1 for Fall, November 1 for Spring, and March
                    1 for Summer. For Transfers, the deadlines are July 1 for Fall, November 1
                    for Spring, and March 1 for Summer. \n
                    """,
                "keywords": "Tuition, Degree Requirements, Undergraduate Application Deadlines",
            }
        ]
