#!/usr/bin/env python3
"""Markdown→HTML変換のWebサービス。`python app.py` で起動する。"""
import os
from pathlib import Path

from flask import Flask, Response, render_template_string, request

from convert import build_from_texts

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

INDEX = """<!DOCTYPE html>
<html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Markdown → HTML 変換</title>
<style>body{font-family:sans-serif;max-width:640px;margin:3rem auto;padding:0 1rem}
label{display:block;margin:1rem 0 .3rem}button{margin-top:1.5rem;padding:.5rem 1.2rem}
input[type=text]{width:100%;padding:.4rem;box-sizing:border-box}</style></head>
<body><h1>Markdown → HTML 変換</h1>
<form method="post" action="/convert" enctype="multipart/form-data">
<label>Markdownファイル（複数選択可）</label>
<input type="file" name="files" accept=".md,.markdown,.txt" multiple required>
<label>タイトル</label><input type="text" name="title" value="説明書">
<label><input type="checkbox" name="download" value="1"> ダウンロードする</label>
<button type="submit">変換</button></form></body></html>"""


@app.get("/")
def index():
    return render_template_string(INDEX)


@app.get("/healthz")
def healthz():
    return "ok"


@app.post("/convert")
def convert():
    items = []
    for f in request.files.getlist("files"):
        if not f.filename:
            continue
        try:
            text = f.read().decode("utf-8-sig")
        except UnicodeDecodeError:
            return "UTF-8のファイルを指定してください", 400
        items.append((Path(f.filename).stem, text))
    if not items:
        return "Markdownファイルを選択してください", 400
    title = request.form.get("title") or "説明書"
    resp = Response(build_from_texts(items, title), mimetype="text/html")
    if request.form.get("download"):
        resp.headers["Content-Disposition"] = 'attachment; filename="output.html"'
    return resp


if __name__ == "__main__":
    app.run(
        host=os.environ.get("HOST", "0.0.0.0"),
        port=int(os.environ.get("PORT", "8000")),
    )
