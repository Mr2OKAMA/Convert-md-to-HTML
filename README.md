# Convert-md-to-HTML
markdownの説明書をHTML形式で見やすくする

## 使い方

```
pip install -r requirements.txt
python convert.py manual1.md manual2.md -o output.html -t "説明書"
```

複数のMarkdownを1つのHTMLにまとめ、タブで切り替えて閲覧できます。
デザインは `template.html` で編集できます（`{{TITLE}}` `{{TABS}}` `{{PANELS}}` が置換されます）。

## Webサービスとして使う

```
pip install -r requirements.txt
python app.py        # http://localhost:8000 （環境変数 HOST / PORT で変更可）
```

ブラウザでMarkdownファイルをアップロードすると、タブ付きHTMLが表示（またはダウンロード）されます。
本番運用では `gunicorn app:app` などのWSGIサーバーを使ってください。

## 公開サイト（GitHub Pages）

`index.html` がトップページです。ブラウザ上でMarkdownをアップロードしてHTMLに変換できます（`template.html` は変換時に読み込まれる部品で、トップには表示されません）。
