import yaml

from constants.constants import TEST_SPECIFICATION_FILE


class SpecificationLoader:
    @staticmethod
    def load():
        with TEST_SPECIFICATION_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:
            return yaml.safe_load(file) or {}
