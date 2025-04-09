# services/code_converter.py

from config.llm_config import llm_config
from utils.quick_convert_prompts import get_specialized_prompt

class CodeConverter:
    def __init__(self):
        self.agent = llm_config.get_phi_agent

    def convert(self, angular_code: str, file_types: list[str]) -> str:
        if not angular_code.strip():
            raise ValueError("angular_code field is required")

        if not file_types:
            raise ValueError("At least one file type must be selected")

        prompt = get_specialized_prompt(file_types, angular_code)
        response = self.agent.run(prompt, stream=False)

        return response.content
