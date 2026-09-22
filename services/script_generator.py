import ast
import logging

from playwright.sync_api import sync_playwright

from config import settings
from services.gemini_service import GeminiService


logger = logging.getLogger(__name__)


class ScriptGenerator:
    def __init__(self, gemini_service: GeminiService):
        self.gemini_service = gemini_service

    def generate(
        self,
        base_url,
        test_cases,
        discovery_data,
        testing_mode,
        repair_feedback=None,
    ):
        scripts = self.gemini_service.generate_test_scripts(
            base_url=base_url,
            approved_test_cases=test_cases,
            discovery_data=discovery_data,
            testing_mode=testing_mode,
            repair_feedback=repair_feedback,
        )

        if "ui_script" in scripts:
            scripts["ui_script"] = self._normalize_python_playwright(
                scripts["ui_script"], discovery_data
            )
            self._validate_script(scripts["ui_script"])
            settings.GENERATED_UI_SCRIPT.write_text(
                scripts["ui_script"], encoding="utf-8"
            )
            self._validate_ui_locators(
                scripts["ui_script"], base_url, discovery_data
            )
        if "api_script" in scripts:
            scripts["api_script"] = self._normalize_python_playwright(
                scripts["api_script"], discovery_data
            )
            self._validate_script(scripts["api_script"])
            settings.GENERATED_API_SCRIPT.write_text(
                scripts["api_script"], encoding="utf-8"
            )

    @staticmethod
    def _validate_script(script):
        tree = ast.parse(script)

        allowed_import_roots = {
            "pytest", "playwright", "random", "re", "string",
        }
        forbidden_calls = {"eval", "exec", "compile", "__import__"}
        forbidden_modules = {
            "os", "subprocess", "shutil", "socket", "requests",
            "urllib", "pathlib", "sys",
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".")[0]
                    if root not in allowed_import_roots:
                        raise ValueError(
                            f"Generated script imports unsupported module: {alias.name}"
                        )

            elif isinstance(node, ast.ImportFrom) and node.module:
                root = node.module.split(".")[0]
                if root in forbidden_modules or root not in allowed_import_roots:
                    raise ValueError(
                        f"Generated script imports unsupported module: {node.module}"
                    )

            elif isinstance(node, ast.Call):
                if (
                    isinstance(node.func, ast.Name)
                    and node.func.id in forbidden_calls
                ):
                    raise ValueError(
                        f"Generated script contains forbidden call: {node.func.id}"
                    )

    @staticmethod
    def _validate_ui_locators(script, base_url, discovery_data):
        locator_calls = list({
            (
                call["method"],
                call["value"],
                tuple(sorted(call["kwargs"].items())),
            ): call
            for call in ScriptGenerator._extract_locator_calls(script)
        }.values())
        if not locator_calls:
            return

        discovered_urls = [
            page.get("url")
            for page in discovery_data.get("ui_pages", [])
            if page.get("url")
        ]
        urls = list(dict.fromkeys([base_url, *discovered_urls]))
        failures = []

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            try:
                matches_by_locator = {id(call): [] for call in locator_calls}
                for url in urls:
                    try:
                        page.goto(
                            url,
                            wait_until="domcontentloaded",
                            timeout=10000,
                        )
                        for locator_call in locator_calls:
                            count = ScriptGenerator._resolve_locator(
                                page, locator_call
                            )
                            if count:
                                matches_by_locator[id(locator_call)].append(
                                    (url, count)
                                )
                    except Exception as exc:
                        logger.debug(
                            "Could not probe locators on %s: %s", url, exc
                        )

                for locator_call in locator_calls:
                    matches = matches_by_locator[id(locator_call)]
                    if not matches:
                        failures.append(
                            f"{locator_call['display']} did not match any discovered page"
                        )
                    elif max(count for _, count in matches) > 1:
                        failures.append(
                            f"{locator_call['display']} matched multiple elements"
                        )
            finally:
                browser.close()

        if failures:
            logger.warning(
                "Generated UI locator validation found possible issues:\n- %s",
                "\n- ".join(failures),
            )

    @staticmethod
    def _normalize_python_playwright(script, discovery_data=None):
        tree = ast.parse(script)

        class PlaywrightPythonNormalizer(ast.NodeTransformer):
            assertion_names = {
                "toBeVisible": "to_be_visible",
                "toHaveURL": "to_have_url",
                "toContainText": "to_contain_text",
                "to_url": "to_have_url",
            }
            locator_methods = {
                "get_by_role", "get_by_label", "get_by_placeholder",
                "get_by_text", "get_by_alt_text", "get_by_title",
                "get_by_test_id",
            }

            def visit_Attribute(self, node):
                node = self.generic_visit(node)
                node.attr = self.assertion_names.get(node.attr, node.attr)
                return node

            def visit_Call(self, node):
                node = self.generic_visit(node)
                if (
                    isinstance(node.func, ast.Attribute)
                    and node.func.attr == "expect"
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "page"
                ):
                    node.func = ast.Name(id="expect", ctx=ast.Load())
                if (
                    isinstance(node.func, ast.Attribute)
                    and node.func.attr in self.locator_methods
                    and len(node.args) == 2
                    and isinstance(node.args[1], ast.Dict)
                    and not node.keywords
                ):
                    keyword_nodes = []
                    for key, value in zip(node.args[1].keys, node.args[1].values):
                        if not isinstance(key, ast.Constant) or not isinstance(key.value, str):
                            return node
                        keyword_nodes.append(ast.keyword(arg=key.value, value=value))
                    node.args = node.args[:1]
                    node.keywords = keyword_nodes
                return node

        normalized = PlaywrightPythonNormalizer().visit(tree)
        if discovery_data:
            normalized = ScriptGenerator._replace_invented_locators(
                normalized, discovery_data
            )
        uses_re = any(
            isinstance(node, ast.Name) and node.id == "re"
            for node in ast.walk(normalized)
        )
        imports_re = any(
            isinstance(node, ast.Import)
            and any(alias.name == "re" for alias in node.names)
            for node in normalized.body
        )
        if uses_re and not imports_re:
            normalized.body.insert(0, ast.Import(names=[ast.alias(name="re")]))
        ast.fix_missing_locations(normalized)
        return ast.unparse(normalized)

    @staticmethod
    def _replace_invented_locators(tree, discovery_data):
        dictionary = discovery_data.get("locator_dictionary", {})
        by_value = {
            entry.get("value"): entry
            for entry in dictionary.values()
            if entry.get("method") == "locator"
        }
        by_key = {
            key: entry for key, entry in dictionary.items()
        }
        links = {}
        for page in discovery_data.get("ui_pages", []):
            for link in page.get("links", []):
                href = link.get("href", "").split(";jsessionid", 1)[0]
                text = link.get("text", "").strip()
                if href and text:
                    links[href.rsplit("/", 1)[-1]] = text

        class LocatorRepair(ast.NodeTransformer):
            def visit_Call(self, node):
                node = self.generic_visit(node)
                if (
                    isinstance(node.func, ast.Attribute)
                    and node.func.attr == "locator"
                    and node.args
                    and isinstance(node.args[0], ast.Constant)
                    and isinstance(node.args[0].value, str)
                ):
                    selector = node.args[0].value
                    entry = by_value.get(selector)
                    if not entry:
                        for prefix in ("input[name='", "input[id='"):
                            if selector.startswith(prefix) and selector.endswith("']"):
                                field = selector[len(prefix):-2]
                                entry = by_key.get(field)
                                if not entry:
                                    entry = next(
                                        (
                                            candidate
                                            for candidate in by_key.values()
                                            if field in candidate.get("value", "")
                                        ),
                                        None,
                                    )
                                break
                    if entry:
                        node.args[0] = ast.Constant(value=entry["value"])
                    elif selector.startswith("input[value='") and selector.endswith("']"):
                        button_name = selector[len("input[value='"):-2]
                        entry = by_key.get(f"button:{button_name}")
                        if entry and entry.get("method") == "get_by_role":
                            node.func = ast.Attribute(
                                value=ast.Name(id="page", ctx=ast.Load()),
                                attr="get_by_role",
                                ctx=ast.Load(),
                            )
                            node.args = [ast.Constant(value="button")]
                            node.keywords = [
                                ast.keyword(
                                    arg="name", value=ast.Constant(value=button_name)
                                ),
                                ast.keyword(arg="exact", value=ast.Constant(value=True)),
                            ]
                    elif selector.startswith("a[href='") and selector.endswith("']"):
                        target = selector[len("a[href='"):-2]
                        link_text = links.get(target)
                        if link_text:
                            node.func = ast.Attribute(
                                value=ast.Name(id="page", ctx=ast.Load()),
                                attr="get_by_role",
                                ctx=ast.Load(),
                            )
                            node.args = [
                                ast.Constant(value="link"),
                            ]
                            node.keywords = [
                                ast.keyword(
                                    arg="name", value=ast.Constant(value=link_text)
                                ),
                                ast.keyword(arg="exact", value=ast.Constant(value=True)),
                            ]
                return node

        return LocatorRepair().visit(tree)

    @staticmethod
    def _extract_locator_calls(script):
        tree = ast.parse(script)
        calls = []
        supported = {
            "locator", "get_by_role", "get_by_label", "get_by_placeholder",
            "get_by_text", "get_by_alt_text", "get_by_title", "get_by_test_id",
        }

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if not isinstance(node.func, ast.Attribute):
                continue
            if node.func.attr not in supported or not node.args:
                continue
            value = ScriptGenerator._literal_value(node.args[0])
            if value is None:
                continue
            display = f"{node.func.attr}({value!r})"
            kwargs = {}
            for keyword in node.keywords:
                keyword_value = ScriptGenerator._literal_value(keyword.value)
                if keyword_value is not None:
                    kwargs[keyword.arg] = keyword_value
            if kwargs:
                display = f"{display}, {kwargs!r}"
            calls.append({
                "method": node.func.attr,
                "value": value,
                "kwargs": kwargs,
                "display": display,
            })
        return calls

    @staticmethod
    def _literal_value(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        return None

    @staticmethod
    def _resolve_locator(page, locator_call):
        method = locator_call["method"]
        value = locator_call["value"]
        if method == "locator":
            return page.locator(value).count()
        return getattr(page, method)(
            value, **locator_call.get("kwargs", {})
        ).count()
