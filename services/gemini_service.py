import json

from google import genai
from google.genai import types

from config import settings


class GeminiService:
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY is not set. "
                "Please add it to the .env file."
            )

        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = settings.GEMINI_MODEL

    def _read_prompt(self, filename):
        return (settings.PROMPT_DIR / filename).read_text(encoding="utf-8")

    def _generate_json(self, prompt):
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            ),
        )
        return self._parse_json(response.text)

    @staticmethod
    def _parse_json(response_text):
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "Gemini returned invalid JSON.\n\n"
                f"Response:\n{response_text}"
            ) from exc

    def generate_test_cases(
        self, base_url, specification, discovered_data, testing_mode
    ):
        prompt = self._read_prompt("test_case_prompt.txt")
        prompt = prompt.replace("{base_url}", base_url)
        prompt = prompt.replace("{testing_mode}", testing_mode)
        prompt = prompt.replace(
            "{test_specification}",
            json.dumps(specification, indent=2),
        )
        prompt = prompt.replace(
            "{discovery_data}",
            json.dumps(discovered_data, indent=2),
        )
        return self._generate_json(prompt)

    def revise_test_cases(
        self,
        base_url,
        current_test_cases,
        feedback,
        specification,
        discovered_data,
        testing_mode,
    ):
        prompt = self._read_prompt("test_case_feedback_prompt.txt")
        prompt = prompt.replace("{base_url}", base_url)
        prompt = prompt.replace("{testing_mode}", testing_mode)
        prompt = prompt.replace(
            "{current_test_cases}",
            json.dumps(current_test_cases, indent=2),
        )
        prompt = prompt.replace("{feedback}", feedback)
        prompt = prompt.replace(
            "{test_specification}",
            json.dumps(specification, indent=2),
        )
        prompt = prompt.replace(
            "{discovery_data}",
            json.dumps(discovered_data, indent=2),
        )
        return self._generate_json(prompt)

    def generate_test_scripts(
        self,
        base_url,
        approved_test_cases,
        discovery_data,
        testing_mode,
        repair_feedback=None,
    ):
        prompt = self._read_prompt("test_script_prompt.txt")
        prompt = prompt.replace("{base_url}", base_url)
        prompt = prompt.replace("{testing_mode}", testing_mode)
        prompt = prompt.replace(
            "{approved_test_cases}",
            json.dumps(approved_test_cases, indent=2),
        )
        prompt = prompt.replace(
            "{discovery_data}",
            json.dumps(discovery_data, indent=2),
        )
        prompt = prompt.replace(
            "{repair_feedback}",
            repair_feedback or "No previous execution failure. Generate the initial script.",
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        return self._split_scripts(response.text, testing_mode)

    @staticmethod
    def _split_scripts(response_text, testing_mode):
        scripts = {}
        if "UI" in testing_mode:
            scripts["ui_script"] = GeminiService._section(
                response_text, "===UI_SCRIPT===", "===API_SCRIPT==="
            )
        if "API" in testing_mode:
            scripts["api_script"] = GeminiService._section(
                response_text, "===API_SCRIPT===", None
            )
        return scripts

    @staticmethod
    def _section(response_text, marker, next_marker):
        if marker not in response_text:
            raise ValueError(f"Gemini response does not contain {marker}.")
        section = response_text.split(marker, 1)[1]
        if next_marker and next_marker in section:
            section = section.split(next_marker, 1)[0]
        return GeminiService._clean_code(section)

    @staticmethod
    def _clean_code(code):
        code = code.strip()

        if code.startswith("```python"):
            code = code[len("```python"):].lstrip()
        elif code.startswith("```"):
            code = code[3:].lstrip()

        if code.endswith("```"):
            code = code[:-3].rstrip()

        return code
