# Convert-md-to-HTML
markdownの説明書をHTML形式で見やすくする

## 使い方

```
pip install -r requirements.txt
python convert.py manual1.md manual2.md -o output.html -t "説明書"
```

複数のMarkdownを1つのHTMLにまとめ、タブで切り替えて閲覧できます。
デザインは `template.html` で編集できます（`{{TITLE}}` `{{TABS}}` `{{PANELS}}` が置換されます）。
