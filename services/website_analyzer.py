import logging
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

from config import settings


logger = logging.getLogger(__name__)


class WebsiteAnalyzer:
    """Discover basic UI information and observed same-origin API calls."""

    def analyze(self, base_url: str, specification: dict) -> dict:
        ui_pages = []
        api_endpoints = {}

        discovery_config = specification.get("discovery", {})
        max_pages = discovery_config.get("max_pages", 8)
        capture_api_calls = discovery_config.get("capture_api_calls", True)
        same_origin_only = discovery_config.get("same_origin_only", True)

        base_parsed = urlparse(base_url)
        allowed_host = base_parsed.netloc

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            def capture_response(response):
                if not capture_api_calls:
                    return

                request = response.request
                if request.resource_type not in {"xhr", "fetch"}:
                    return

                parsed = urlparse(response.url)
                if same_origin_only and parsed.netloc != allowed_host:
                    return

                key = (request.method.upper(), response.url)
                api_endpoints[key] = {
                    "method": request.method.upper(),
                    "url": response.url,
                    "resource_type": request.resource_type,
                    "status": response.status,
                }

            page.on("response", capture_response)

            try:
                self._visit_page(page, base_url, ui_pages)

                links = page.locator("a").evaluate_all(
                    """
                    elements => elements
                        .map(a => a.href)
                        .filter(Boolean)
                    """
                )

                visited = {page.url}

                for href in links:
                    if len(ui_pages) >= max_pages:
                        break

                    parsed = urlparse(href)

                    if same_origin_only and parsed.netloc != allowed_host:
                        continue

                    if href in visited:
                        continue

                    visited.add(href)

                    try:
                        self._visit_page(page, href, ui_pages)
                    except Exception as exc:
                        logger.warning(
                            "Could not inspect %s: %s",
                            href,
                            exc,
                        )
            finally:
                context.close()
                browser.close()

        result = {
            "ui_pages": ui_pages,
            "api_endpoints": list(api_endpoints.values()),
        }

        settings.DISCOVERY_FILE.write_text(
            self._pretty_json(result),
            encoding="utf-8",
        )

        return result

    @staticmethod
    def _visit_page(page, url, ui_pages):
        page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=30000,
        )
        page.wait_for_timeout(1000)
        ui_pages.append(WebsiteAnalyzer._extract_page(page))

    @staticmethod
    def _extract_page(page) -> dict:
        return {
            "url": page.url,
            "title": page.title(),
            "headings": page.locator("h1,h2,h3").all_inner_texts()[:30],
            "links": page.locator("a").all_inner_texts()[:50],
            "buttons": page.locator(
                "button,input[type=button],input[type=submit]"
            ).all_inner_texts()[:30],
            "locator_candidates": page.locator(
                "button,input,textarea,select,a"
            ).evaluate_all(
                """
                elements => elements.slice(0, 100).map(e => ({
                    tag: e.tagName.toLowerCase(),
                    role: e.getAttribute("role") || "",
                    name: e.getAttribute("aria-label") || "",
                    text: (e.innerText || e.value || "").trim().slice(0, 120),
                    id: e.id || "",
                    test_id: e.getAttribute("data-testid") || "",
                    name_attribute: e.getAttribute("name") || "",
                    placeholder: e.getAttribute("placeholder") || ""
                }))
                """
            ),
            "inputs": page.locator(
                "input,textarea,select"
            ).evaluate_all(
                """
                elements => elements.map(e => ({
                    tag: e.tagName,
                    type: e.type || "",
                    name: e.name || "",
                    id: e.id || "",
                    placeholder: e.placeholder || "",
                    label: e.getAttribute("aria-label") || ""
                }))
                """
            )[:50],
            "forms": page.locator("form").evaluate_all(
                """
                elements => elements.map(f => ({
                    action: f.action || "",
                    method: f.method || "get"
                }))
                """
            )[:20],
        }

    @staticmethod
    def _pretty_json(data):
        import json
        return json.dumps(data, indent=2, ensure_ascii=False)
