#!/usr/bin/env python3
"""複数のMarkdownファイルを、タブ切り替え付きの1つのHTMLに変換する。

使い方: python convert.py a.md b.md -o output.html [-t タイトル]
"""
import argparse
import html
import re
from pathlib import Path

import markdown

TEMPLATE = Path(__file__).with_name("template.html")


def title_of(path: Path, text: str) -> str:
    m = re.search(r"^#\s+(.+)$", text, re.M)
    return m.group(1).strip() if m else path.stem


def build(files, title):
    return build_from_texts(
        [(f.stem, f.read_text(encoding="utf-8")) for f in files], title
    )


def build_from_texts(items, title):
    """items: (名前, Markdown本文) のリストからHTML文字列を生成する。"""
    tabs, panels = [], []
    for i, (name, text) in enumerate(items):
        body = markdown.markdown(
            text, extensions=["fenced_code", "tables", "toc", "sane_lists"]
        )
        pid = f"tab{i}"
        tabs.append(
            f'<button class="tab" role="tab" data-target="{pid}">'
            f"{html.escape(name)}</button>"
        )
        panels.append(f'<section class="panel" id="{pid}" role="tabpanel">{body}</section>')
    out = TEMPLATE.read_text(encoding="utf-8")
    # 置換は1回で行い、本文中の {{...}} が再置換されないようにする
    values = {
        "TITLE": html.escape(title),
        "TABS": "\n".join(tabs),
        "PANELS": "\n".join(panels),
    }
    return re.sub(r"\{\{(TITLE|TABS|PANELS)\}\}", lambda m: values[m.group(1)], out)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("files", nargs="+", type=Path, help="入力Markdownファイル")
    ap.add_argument("-o", "--output", type=Path, default=Path("output.html"))
    ap.add_argument("-t", "--title", default="説明書")
    a = ap.parse_args()
    a.output.write_text(build(a.files, a.title), encoding="utf-8")
    print(f"生成しました: {a.output}")


if __name__ == "__main__":
    main()
