# Databricks notebook source
# MAGIC %md
# MAGIC # Document renderer helper
# MAGIC
# MAGIC This helper renders page images produced by `ai_parse_document` and overlays
# MAGIC the extracted element bounding boxes. It is deliberately self-contained so
# MAGIC the main notebook has no dependency on an external tutorial workspace.

# COMMAND ----------

import base64
import html
import json
import mimetypes
import os
from collections import Counter
from typing import Any, Dict, Iterable, List, Optional, Tuple

from IPython.display import HTML, display


class DocumentRenderer:
    """Render ai_parse_document JSON output with visual bounding-box overlays."""

    TYPE_COLORS = {
        "title": "#7c3aed",
        "section_header": "#2563eb",
        "text": "#16a34a",
        "table": "#ea580c",
        "figure": "#db2777",
        "caption": "#0891b2",
        "page_header": "#6b7280",
        "page_footer": "#6b7280",
        "page_number": "#6b7280",
        "footnote": "#6b7280",
    }

    def _normalize_result(self, parsed_result: Any) -> Dict[str, Any]:
        """Convert supported JSON-like inputs into a plain Python dictionary."""
        if isinstance(parsed_result, dict):
            return parsed_result
        if isinstance(parsed_result, str):
            return json.loads(parsed_result)
        if hasattr(parsed_result, "asDict"):
            return parsed_result.asDict(recursive=True)
        raise TypeError("parsed_result must be a dictionary, JSON string, or Row-like object.")

    def _parse_page_selection(self, page_selection: Optional[str], page_ids: Iterable[int]) -> List[int]:
        """Parse a human-friendly page selector such as '1,3-5' into zero-based page IDs."""
        available = sorted(page_ids)
        if page_selection is None or str(page_selection).strip().lower() in {"", "all"}:
            return available
        chosen = set()
        for token in str(page_selection).split(","):
            token = token.strip()
            if not token:
                continue
            if "-" in token:
                start_text, end_text = token.split("-", 1)
                start, end = int(start_text), int(end_text)
                chosen.update(range(start - 1, end))
            else:
                chosen.add(int(token) - 1)
        return [page_id for page_id in available if page_id in chosen]

    def _image_data_uri(self, image_uri: str) -> Optional[str]:
        """Load a rendered page image from a Unity Catalog volume as a data URI."""
        if not image_uri or not os.path.isfile(image_uri):
            return None
        mime_type = mimetypes.guess_type(image_uri)[0] or "image/png"
        with open(image_uri, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode("ascii")
        return f"data:{mime_type};base64,{encoded}"

    def _elements_for_page(self, elements: List[Dict[str, Any]], page_id: int) -> List[Tuple[Dict[str, Any], List[float]]]:
        """Return elements whose bounding-box metadata belongs to the requested page."""
        matches = []
        for element in elements:
            for box in element.get("bbox") or []:
                if box.get("page_id") == page_id and len(box.get("coord") or []) >= 4:
                    matches.append((element, box["coord"][:4]))
                    break
        return matches

    def _overlay_markup(self, element: Dict[str, Any], coordinates: List[float], canvas_width: float, canvas_height: float) -> str:
        """Create one escaped SVG rectangle and tooltip for a parsed document element."""
        left, top, right, bottom = [float(value) for value in coordinates]
        x, y = min(left, right), min(top, bottom)
        width, height = max(abs(right - left), 2), max(abs(bottom - top), 2)
        element_type = str(element.get("type") or "unknown")
        color = self.TYPE_COLORS.get(element_type, "#64748b")
        content = str(element.get("content") or element.get("description") or "No extracted text")
        tooltip = html.escape(f"{element_type} | ID {element.get('id', '?')} | confidence {element.get('confidence', 'n/a')}\n{content[:700]}")
        label = html.escape(element_type.replace("_", " "))
        return (
            f'<g class="parse-box"><title>{tooltip}</title>'
            f'<rect x="{x}" y="{y}" width="{width}" height="{height}" '
            f'fill="{color}" fill-opacity="0.12" stroke="{color}" stroke-width="{max(canvas_width, canvas_height) * 0.0025}" rx="3" />'
            f'<text x="{x + 3}" y="{max(y + 12, 12)}" fill="{color}" font-size="12" font-family="Arial, sans-serif" font-weight="700">{label}</text>'
            "</g>"
        )

    def _page_markup(self, page: Dict[str, Any], page_elements: List[Tuple[Dict[str, Any], List[float]]]) -> str:
        """Build the HTML panel for one page image and its parsed elements."""
        page_id = int(page.get("id", 0))
        image_uri = page.get("image_uri")
        image_data = self._image_data_uri(image_uri)
        if not image_data:
            safe_uri = html.escape(str(image_uri or "missing image_uri"))
            return f'<div class="notice">Page {page_id + 1}: rendered image unavailable at <code>{safe_uri}</code>.</div>'
        all_coordinates = [coordinate for _, box in page_elements for coordinate in box]
        canvas_width = max([coordinate for index, coordinate in enumerate(all_coordinates) if index % 4 in {0, 2}] or [1000])
        canvas_height = max([coordinate for index, coordinate in enumerate(all_coordinates) if index % 4 in {1, 3}] or [1400])
        overlays = "".join(self._overlay_markup(element, box, canvas_width, canvas_height) for element, box in page_elements)
        element_cards = []
        for element, _ in page_elements:
            element_type = str(element.get("type") or "unknown")
            color = self.TYPE_COLORS.get(element_type, "#64748b")
            content = html.escape(str(element.get("content") or element.get("description") or "No extracted text"))
            confidence = html.escape(str(element.get("confidence", "n/a")))
            element_cards.append(
                f'<details><summary style="color:{color}">{html.escape(element_type)} - ID {html.escape(str(element.get("id", "?")))}, confidence {confidence}</summary>'
                f'<pre>{content}</pre></details>'
            )
        return f'''<section class="page-panel">
  <h3>Page {page_id + 1} <span>{len(page_elements)} parsed element(s)</span></h3>
  <div class="page-canvas">
    <img src="{image_data}" alt="Rendered source page {page_id + 1}" />
    <svg viewBox="0 0 {canvas_width} {canvas_height}" preserveAspectRatio="none" aria-label="Parsed element overlays">{overlays}</svg>
  </div>
  <div class="element-list">{''.join(element_cards) or '<p>No bounding boxes were returned for this page.</p>'}</div>
</section>'''

    def render_document(self, parsed_result: Any, page_selection: Optional[str] = None) -> None:
        """Display selected parsed pages, their source renders, and element overlays."""
        result = self._normalize_result(parsed_result)
        document = result.get("document") or {}
        pages = document.get("pages") or []
        elements = document.get("elements") or []
        metadata = result.get("metadata") or {}
        selected_ids = self._parse_page_selection(page_selection, [int(page.get("id", index)) for index, page in enumerate(pages)])
        type_counts = Counter(str(element.get("type") or "unknown") for element in elements)
        legend = "".join(
            f'<span><i style="background:{self.TYPE_COLORS.get(element_type, "#64748b")}"></i>{html.escape(element_type)}</span>'
            for element_type in sorted(type_counts)
        )
        panels = []
        for index, page in enumerate(pages):
            page_id = int(page.get("id", index))
            if page_id in selected_ids:
                panels.append(self._page_markup(page, self._elements_for_page(elements, page_id)))
        style = """
<style>
.document-renderer {font-family:Arial,sans-serif;color:#25232a;max-width:1080px;margin:10px auto;}
.document-renderer .summary {background:#f5f3ff;border:1px solid #ddd6fe;border-radius:10px;padding:14px 18px;margin-bottom:14px;}
.document-renderer .legend span {display:inline-flex;align-items:center;margin:6px 14px 0 0;font-size:12px}.document-renderer .legend i{width:10px;height:10px;border-radius:50%;display:inline-block;margin-right:5px}
.document-renderer .page-panel {border:1px solid #e6e2dc;border-radius:10px;padding:16px;margin:18px 0;background:#fff;}.document-renderer h3{margin:0 0 12px}.document-renderer h3 span{font-weight:normal;color:#6b7280;font-size:13px}
.document-renderer .page-canvas {position:relative;max-width:860px;margin:auto;background:#f1f1f1}.document-renderer .page-canvas img{display:block;width:100%;height:auto}.document-renderer .page-canvas svg{position:absolute;inset:0;width:100%;height:100%}.document-renderer .parse-box{cursor:help}.document-renderer details{border-top:1px solid #ebe7e1;padding:8px 0}.document-renderer summary{cursor:pointer;font-weight:700}.document-renderer pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#faf8f5;padding:8px;border-radius:5px;font-size:12px}.document-renderer .notice{padding:16px;background:#fff7ed;border:1px solid #fed7aa;border-radius:8px}
</style>"""
        document_id = html.escape(str(metadata.get("id", "not supplied")))
        summary = f'<div class="summary"><strong>DocumentRenderer</strong><br>Document ID: <code>{document_id}</code> | pages shown: {len(panels)} | total elements: {len(elements)}<div class="legend">{legend}</div></div>'
        display(HTML(f'<div class="document-renderer">{style}{summary}{"".join(panels) or "<p>No selected pages were available.</p>"}</div>'))


def render_ai_parse_output(parsed_result: Any, page_selection: Optional[str] = None) -> None:
    """Render one ai_parse_document result with page images and bounding boxes."""
    DocumentRenderer().render_document(parsed_result, page_selection)
