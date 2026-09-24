import json
import logging
from urllib.parse import urljoin, urlparse

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from constants.constants import MCP_SERVER_COMMAND, MCP_SERVER_PACKAGE


logger = logging.getLogger(__name__)


class McpPlaywrightDiscovery:
    """Crawl pages and collect locator expressions through Playwright MCP."""

    async def analyze(self, base_url: str, specification: dict) -> dict:
        server = StdioServerParameters(
            command=MCP_SERVER_COMMAND,
            args=["-y", MCP_SERVER_PACKAGE],
        )

        async with stdio_client(server) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                tools = await session.list_tools()
                tool_names = {tool.name for tool in tools.tools}
                navigate = self._find_tool(
                    tool_names, "browser_navigate", "playwright_navigate"
                )
                snapshot = self._find_tool(
                    tool_names, "browser_snapshot", "playwright_snapshot"
                )
                evaluate = self._find_tool(
                    tool_names, "browser_evaluate", "playwright_evaluate"
                )
                if not navigate or not snapshot or not evaluate:
                    raise RuntimeError(
                        "Playwright MCP does not expose navigate, snapshot, and "
                        "evaluate tools"
                    )

                max_pages = specification.get("discovery", {}).get(
                    "max_pages", 8
                )
                pages = []
                pending_urls = [base_url]
                visited_urls = set()
                base_origin = urlparse(base_url).netloc

                while pending_urls and len(pages) < max_pages:
                    url = pending_urls.pop(0)
                    normalized_url = url.split("#", 1)[0]
                    if normalized_url in visited_urls:
                        continue
                    if urlparse(normalized_url).netloc != base_origin:
                        continue
                    visited_urls.add(normalized_url)

                    await session.call_tool(
                        navigate,
                        arguments={"url": normalized_url},
                    )
                    snapshot_text = self._result_text(
                        await session.call_tool(snapshot, arguments={})
                    )
                    locator_result = await session.call_tool(
                        evaluate,
                        arguments={"function": self._locator_script()},
                    )
                    locator_data = self._result_json(locator_result)
                    page_url = locator_data.get("url", normalized_url)
                    pages.append(
                        {
                            "url": page_url,
                            "title": locator_data.get("title", ""),
                            "headings": locator_data.get("headings", []),
                            "links": locator_data.get("links", []),
                            "buttons": locator_data.get("buttons", []),
                            "inputs": locator_data.get("inputs", []),
                            "forms": [],
                            "locator_candidates": locator_data.get(
                                "locator_candidates", []
                            ),
                            "accessibility_snapshot": snapshot_text,
                        }
                    )

                    for link in locator_data.get("links", []):
                        next_url = urljoin(page_url, link.get("href", ""))
                        if urlparse(next_url).netloc == base_origin:
                            pending_urls.append(next_url)

        locator_dictionary = self._build_locator_dictionary(pages)

        return {
            "ui_pages": pages,
            "locator_dictionary": locator_dictionary,
            "api_endpoints": [],
            "mcp_tools": sorted(tool_names),
        }

    @staticmethod
    def _find_tool(tool_names, *candidates):
        return next((name for name in candidates if name in tool_names), None)

    @staticmethod
    def _result_text(result):
        parts = []
        for item in getattr(result, "content", []):
            text = getattr(item, "text", None)
            if text:
                parts.append(text)
        if not parts:
            raise RuntimeError("Playwright MCP returned an empty snapshot")
        return "\n".join(parts)

    @staticmethod
    def _result_json(result):
        text = McpPlaywrightDiscovery._result_text(result)
        if "### Result" in text:
            text = text.split("### Result", 1)[1].split("\n", 1)[-1].strip()
        try:
            value, _ = json.JSONDecoder().raw_decode(text)
            if isinstance(value, str):
                value = json.loads(value)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "Playwright MCP returned invalid locator data: " + text
            ) from exc
        if not isinstance(value, dict):
            raise RuntimeError("Playwright MCP locator data must be an object")
        return value

    @staticmethod
    def _build_locator_dictionary(pages):
        dictionary = {}
        for page in pages:
            for candidate in page.get("locator_candidates", []):
                key = candidate.get("key")
                if key and key not in dictionary:
                    dictionary[key] = {
                        "url": page.get("url"),
                        "method": candidate.get("method"),
                        "value": candidate.get("value"),
                        "kwargs": candidate.get("kwargs", {}),
                        "playwright": candidate.get("playwright"),
                    }
        return dictionary

    @staticmethod
    def _locator_script():
        return """
() => {
    const quote = (value) => JSON.stringify(value);
    const clean = (value) => (value || '').replace(/\\s+/g, ' ').trim();
    const visible = (element) => {
        const style = window.getComputedStyle(element);
        return style.display !== 'none' && style.visibility !== 'hidden' &&
            element.getBoundingClientRect().width > 0;
    };
    const labelFor = (element) => {
        if (element.labels && element.labels.length) return clean(element.labels[0].innerText);
        if (element.id) {
            const label = document.querySelector(`label[for="${CSS.escape(element.id)}"]`);
            if (label) return clean(label.innerText);
        }
        return '';
    };
    const candidates = [];
    const add = (element, method, value, kwargs, key) => {
        if (!value || !key || !visible(element)) return;
        candidates.push({
            key, method, value, kwargs,
            playwright: `page.${method}(${quote(value)}${Object.keys(kwargs).length ? ', ' + JSON.stringify(kwargs) : ''})`
        });
    };
    document.querySelectorAll('input, textarea, select').forEach((element) => {
        const label = labelFor(element);
        const name = element.getAttribute('name');
        const placeholder = element.getAttribute('placeholder');
        const testId = element.getAttribute('data-testid');
        const key = testId || name || label || placeholder || element.id;
        if (testId) add(element, 'get_by_test_id', testId, {}, key);
        else if (label) add(element, 'get_by_label', label, {}, key);
        else if (placeholder) add(element, 'get_by_placeholder', placeholder, {}, key);
        else if (name) add(element, 'locator', `[name="${CSS.escape(name)}"]`, {}, key);
        else if (element.id) add(element, 'locator', `#${CSS.escape(element.id)}`, {}, key);
    });
    document.querySelectorAll('button, input[type="submit"], input[type="button"], a').forEach((element) => {
        const name = clean(element.getAttribute('aria-label') || element.innerText || element.value);
        if (!name || !visible(element)) return;
        const role = element.tagName.toLowerCase() === 'a' ? 'link' : 'button';
        const key = `${role}:${name}`;
        add(element, 'get_by_role', role, {name, exact: true}, key);
    });
    return JSON.stringify({
        url: location.href,
        title: document.title,
        headings: [...document.querySelectorAll('h1,h2,h3')].map((e) => clean(e.innerText)).filter(Boolean),
        links: [...document.querySelectorAll('a[href]')].filter(visible).map((e) => ({href: e.href, text: clean(e.innerText)})),
        buttons: [...document.querySelectorAll('button, input[type="submit"], input[type="button"]')].filter(visible).map((e) => clean(e.innerText || e.value || e.getAttribute('aria-label'))).filter(Boolean),
        inputs: [...document.querySelectorAll('input, textarea, select')].filter(visible).map((e) => ({type: e.type || e.tagName.toLowerCase(), name: e.name || '', label: labelFor(e), placeholder: e.placeholder || ''})),
        locator_candidates: candidates
    });
}
"""
