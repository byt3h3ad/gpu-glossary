# Builds a printable PDF of the GPU Glossary from the markdown sources.
import argparse
import re
import sys
from datetime import date
from pathlib import Path

import frontmatter
import markdown as md
from pygments.formatters import HtmlFormatter
from weasyprint import HTML

from bundle import Page, load_from_contents_path, replace_svgs_with_pngs

HERE = Path(__file__).parent
ROOT = HERE.parent

PAGE_CSS = """
@page {
  size: Letter;
  margin: 1in 0.85in;
  @bottom-center { content: counter(page); font-size: 9pt; color: #666; }
}
body { font-family: "DejaVu Serif", Georgia, serif; font-size: 10.5pt; line-height: 1.5; color: #111; }
h1, h2, h3, h4 { font-family: "DejaVu Sans", Arial, sans-serif; color: #111; page-break-after: avoid; }
h1 { font-size: 26pt; page-break-before: always; margin-top: 0; }
h2 { font-size: 18pt; page-break-before: always; border-bottom: 1px solid #ccc; padding-bottom: 4px; margin-top: 0; }
h3 { font-size: 13pt; margin-top: 1.4em; }
h4 { font-size: 11pt; }
a { color: #0b5fa5; text-decoration: none; }
img { max-width: 100%; }
pre, code { font-family: "DejaVu Sans Mono", monospace; font-size: 8.5pt; }
pre { background: #f5f5f5; padding: 8px; border-radius: 4px; white-space: pre-wrap; overflow-wrap: break-word; page-break-inside: avoid; }
table { border-collapse: collapse; width: 100%; margin: 1em 0; font-size: 9pt; }
th, td { border: 1px solid #ccc; padding: 4px 6px; }
blockquote { color: #555; border-left: 3px solid #ccc; padding-left: 10px; }
"""


def slug_for_href(href: str) -> str:
    return href.rstrip("/").rsplit("/", 1)[-1]


def slugify_fallback(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def collect_hrefs(pages: list[Page]) -> set[str]:
    hrefs = set()
    for p in pages:
        if p.href:
            hrefs.add(p.href)
        hrefs |= collect_hrefs(p.pages)
    return hrefs


def find_all_markdown_hrefs() -> dict[str, Path]:
    """Every *.md under gpu-glossary/, mapped to its /gpu-glossary/... href."""
    out = {}
    for path in (ROOT / "gpu-glossary").rglob("*.md"):
        rel = path.relative_to(ROOT).with_suffix("")
        out["/" + str(rel).replace("\\", "/")] = path
    return out


def titleize(stem: str) -> str:
    upper = {"cuda", "sm", "ptx", "sass", "gpu", "cpu", "tma", "tpc", "gpc",
             "lsu", "sfu", "cutlass", "cute", "nvml", "cupti", "nvrtc"}
    return " ".join(w.upper() if w in upper else w.capitalize() for w in stem.split("-"))


def append_unmapped(pages: list[Page]) -> list[Page]:
    """Auto-append any *.md not covered by contents.json so nothing is ever
    silently dropped from the PDF when upstream adds new pages."""
    known = collect_hrefs(pages)
    unmapped = sorted(h for h in find_all_markdown_hrefs() if h not in known)
    if unmapped:
        print(f"::warning::{len(unmapped)} markdown file(s) missing from "
              f"utils/contents.json, auto-appended under 'Uncategorized': "
              f"{unmapped}", file=sys.stderr)
        extra = [Page(title=titleize(Path(h).stem), href=h, abbreviation=None) for h in unmapped]
        pages.append(Page(title="Uncategorized", href="", abbreviation=None, pages=extra))
    return pages


def render_page_for_pdf(page: Page, level: int = 0) -> str:
    heading = "#" * (2 + min(level, 2))
    slug = slug_for_href(page.href) if page.href else slugify_fallback(page.title)
    out = f'<a id="{slug}"></a>\n\n{heading} {page.title}\n\n'
    if page.href:
        path = (ROOT / page.href.lstrip("/")).with_suffix(".md")
        if path.exists():
            body = frontmatter.load(path).content
            body = re.sub(r"/gpu-glossary/(?:[^/]+/)?([^/\s]+)", r"#\1", body)
            body = body.replace("(themed-image://", "(https://modal-cdn.com/gpu-glossary/light-")
            body = replace_svgs_with_pngs(body)
        else:
            print(f"::warning::source file missing for '{page.href}'; using placeholder", file=sys.stderr)
            body = "_(Source file for this entry was removed upstream; update `utils/contents.json`.)_"
        out += body
    out += "\n\n" + "\n\n".join(render_page_for_pdf(c, level + 1) for c in page.pages)
    return out.strip()


def build_markdown(pages: list[Page]) -> str:
    header = (
        "# GPU Glossary\n\n"
        "Content by [Modal](https://modal.com), from "
        "[modal-labs/gpu-glossary](https://github.com/modal-labs/gpu-glossary), "
        "licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). "
        f"This PDF was generated automatically on {date.today().isoformat()} "
        "and may lag behind the live site at https://modal.com/gpu-glossary.\n\n"
    )
    return header + "\n\n".join(render_page_for_pdf(p) for p in pages)


def markdown_to_html(text: str) -> str:
    body = md.markdown(text, extensions=["extra", "codehilite", "sane_lists"],
                        extension_configs={"codehilite": {"guess_lang": False}})
    pygments_css = HtmlFormatter().get_style_defs(".codehilite")
    return f"<html><head><meta charset='utf-8'><style>{PAGE_CSS}\n{pygments_css}</style></head><body>{body}</body></html>"


def main() -> None:
    p = argparse.ArgumentParser(description="Build a printable PDF of the GPU Glossary.")
    p.add_argument("--contents-json-path", type=Path, default=HERE / "contents.json")
    p.add_argument("--output-pdf", type=Path, default=ROOT / "dist" / "gpu-glossary.pdf")
    p.add_argument("--output-markdown", type=Path, default=ROOT / "dist" / "gpu-glossary.md")
    args = p.parse_args()

    pages = load_from_contents_path(args.contents_json_path)
    pages = append_unmapped(pages)
    markdown_text = build_markdown(pages)

    args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output_markdown.write_text(markdown_text, encoding="utf-8")

    html_text = markdown_to_html(markdown_text)
    HTML(string=html_text, base_url=str(ROOT)).write_pdf(str(args.output_pdf))
    print(args.output_pdf)


if __name__ == "__main__":
    main()
