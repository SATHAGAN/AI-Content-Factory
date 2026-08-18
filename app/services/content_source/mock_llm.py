class MockTopicLLM:
    def generate(self, *, system: str, prompt: str, response_format: str):
        return "A curious little fox learns why the moon changes shape."
