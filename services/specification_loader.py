import yaml

from config import settings


class SpecificationLoader:
    @staticmethod
    def load():
        with settings.TEST_SPECIFICATION_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:
            return yaml.safe_load(file) or {}
