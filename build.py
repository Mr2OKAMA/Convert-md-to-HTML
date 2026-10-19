#!/usr/bin/env python3
"""プロパティと3つのMarkdownを、目次付きのHTML手順書にまとめる。"""
import argparse
import os
import re
from pathlib import Path
from urllib.parse import quote
from xml.etree import ElementTree

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markdown.extensions import Extension
from markdown.extensions.toc import slugify_unicode
from markdown.inlinepatterns import InlineProcessor
from markdown.postprocessors import Postprocessor
from markdown.treeprocessors import Treeprocessor
from markdown.util import AtomicString

from convert import markdown_converter

ROOT = Path(__file__).resolve().parent
TEMPLATES = ROOT / "templates"
SECTIONS = (
    ("mindset", "マインドセット", "1_マインドセット.md"),
    ("workflow", "ワークフロー", "2_ワークフロー.md"),
    ("operations", "オペレーション", "3_オペレーション.md"),
)
PROPERTY_FIELDS = ("作業名", "管理ID", "版数", "作成者", "作成日", "承認者")
HISTORY_FIELDS = ("版数", "日付", "改訂者", "内容")


class ConfirmInlineProcessor(InlineProcessor):
    def handleMatch(self, match, data):
        element = ElementTree.Element("mark", {"class": "confirm"})
        element.text = AtomicString(match.group(0))
        return element, match.start(0), match.end(0)


class MermaidPostprocessor(Postprocessor):
    def run(self, text):
        return re.sub(
            r'<pre><code class="language-mermaid">(.*?)</code></pre>',
            r'<pre class="mermaid">\1</pre>',
            text,
            flags=re.S,
        )


class ProcedurePhotoTreeprocessor(Treeprocessor):
    def run(self, root):
        in_procedure = False
        procedure_heading = None
        for element in root:
            if element.tag in {f"h{level}" for level in range(1, 7)}:
                if in_procedure:
                    if element.tag == procedure_heading:
                        break
                elif "".join(element.itertext()).strip() == "手順":
                    in_procedure = True
                    procedure_heading = element.tag
                continue
            if not in_procedure or element.tag != "ol":
                continue
            element.set("class", "procedure-steps")
            for item in element.findall("li"):
                image = next(item.iter("img"), None)
                caption = "写真を追加"
                if image is not None:
                    caption = image.get("alt", "").strip() or "手順の写真"
                    image.set("alt", caption)
                    image.set("loading", "lazy")
                    parent = next(
                        (node for node in item.iter() if image in list(node)),
                        None,
                    )
                    if parent is not None:
                        parent.remove(image)
                        if parent.tag == "p" and not len(parent) and not (parent.text or "").strip():
                            item.remove(parent)
                figure_class = "step-photo" if image is not None else "step-photo step-photo-placeholder"
                figure = ElementTree.SubElement(item, "figure", {"class": figure_class})
                if image is not None:
                    figure.append(image)
                ElementTree.SubElement(figure, "figcaption").text = caption
        return root


class ProcedureExtension(Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(
            ProcedurePhotoTreeprocessor(md), "procedure_photos", 5
        )
        md.inlinePatterns.register(
            ConfirmInlineProcessor(r"【要確認】", md), "confirm", 65
        )
        md.postprocessors.register(MermaidPostprocessor(md), "mermaid", 25)


def load_properties(folder):
    with (folder / "0_property.yaml").open(encoding="utf-8-sig") as source:
        properties = yaml.safe_load(source)
    if not isinstance(properties, dict) or not properties.get("作業名"):
        raise ValueError("0_property.yamlには作業名を含む項目を指定してください")
    for field in PROPERTY_FIELDS:
        if isinstance(properties.get(field), (dict, list)):
            raise ValueError(f"プロパティの「{field}」は単一の値にしてください")
    history = properties.get("改訂履歴") or []
    if not isinstance(history, list) or any(
        not isinstance(entry, dict) for entry in history
    ):
        raise ValueError("改訂履歴は版数・日付・改訂者・内容のリストにしてください")
    return properties, history


def build(folder, inline_css=False):
    folder = folder.resolve()
    properties, history = load_properties(folder)
    sections = []
    for section_id, title, filename in SECTIONS:
        text = (folder / filename).read_text(encoding="utf-8-sig")
        text = re.sub(r"\A\s*#[ \t]+[^\n]*(?:\n|$)", "", text, count=1)
        converter = markdown_converter(
            extra_extensions=[ProcedureExtension()],
            extension_configs={
                "toc": {
                    "baselevel": 2,
                    "slugify": lambda value, separator, prefix=section_id: (
                        f"{prefix}-{slugify_unicode(value, separator)}"
                    ),
                }
            },
        )
        body = converter.convert(text)
        sections.append(
            {"id": section_id, "title": title, "body": body, "toc": converter.toc}
        )
    environment = Environment(
        loader=FileSystemLoader(TEMPLATES),
        autoescape=select_autoescape(default=True),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    output = environment.get_template("procedure.html.j2").render(
        properties=properties,
        property_fields=PROPERTY_FIELDS,
        history=history,
        history_fields=HISTORY_FIELDS,
        sections=sections,
        inline_css=inline_css,
        css=TEMPLATES.joinpath("style.css").read_text(encoding="utf-8") if inline_css else "",
        css_url=quote(Path(os.path.relpath(TEMPLATES / "style.css", folder)).as_posix()),
    )
    destination = folder / "index.html"
    destination.write_text(output, encoding="utf-8")
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folders", nargs="*", type=Path, help="手順書フォルダ（複数指定可）")
    parser.add_argument("--all", action="store_true", help="samples/*を一括変換")
    parser.add_argument("--inline-css", action="store_true", help="CSSをHTMLに埋め込む")
    args = parser.parse_args()
    if args.all and args.folders:
        parser.error("フォルダ指定と--allは同時に使用できません")
    if not args.all and not args.folders:
        parser.error("手順書フォルダまたは--allを指定してください")
    folders = (
        sorted(path for path in (ROOT / "samples").iterdir() if path.is_dir())
        if args.all else args.folders
    )
    for folder in folders:
        if len(folders) > 1 or args.all:
            if folder.is_dir() and not (folder / "0_property.yaml").exists():
                print(f"スキップ（0_property.yamlなし）: {folder}")
                continue
        try:
            print(f"生成しました: {build(folder, args.inline_css)}")
        except (OSError, ValueError, yaml.YAMLError) as error:
            parser.exit(1, f"変換できませんでした（{folder}）: {error}\n")


if __name__ == "__main__":
    main()
