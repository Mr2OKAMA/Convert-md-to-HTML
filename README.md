# Convert-md-to-HTML

複数のMarkdown説明書を、タブ切り替え付きの1つの見やすいHTMLに変換するツールです。

## 画面・ファイルの確認

| ファイル | 説明 | リンク |
|---|---|---|
| `index.html` | トップページ（ブラウザ上でMarkdownをアップロードして変換） | [index.html](index.html) ・ [ソース表示](https://github.com/Mr2OKAMA/Convert-md-to-HTML/blob/main/index.html) |
| `template.html` | 出力HTMLのデザインテンプレート | [template.html](template.html) ・ [ソース表示](https://github.com/Mr2OKAMA/Convert-md-to-HTML/blob/main/template.html) |

※ GitHub Pages 公開時は `index.html` がトップページになります。`template.html` は変換時に読み込まれる部品で、トップには表示されません。

## 構成

| ファイル | 役割 |
|---|---|
| `convert.py` | コマンドライン変換（複数Markdown → 1つのHTML） |
| `app.py` | Flask製Webサービス（アップロードして変換） |
| `index.html` | 静的な変換ページ（ブラウザ内で変換、`template.html` を読み込む） |
| `template.html` | デザインテンプレート |
| `requirements.txt` | 依存ライブラリ（markdown, flask） |

## 使い方

### 1. コマンドライン

```
pip install -r requirements.txt
python convert.py manual1.md manual2.md -o output.html -t "説明書"
```

### 2. Webサービス

```
python app.py        # http://localhost:8000 （環境変数 HOST / PORT で変更可）
```

ブラウザでMarkdownをアップロードすると、タブ付きHTMLが表示（またはダウンロード）されます。
本番運用では `gunicorn app:app` などのWSGIサーバーを使ってください。

### 3. 静的ページ（GitHub Pages）

`index.html` をブラウザで開く（または公開して利用する）と、ブラウザ上だけでMarkdownをHTMLに変換できます。

## テンプレートの編集

デザインは `template.html` で編集できます。次のプレースホルダーが置換されます。

- `{{TITLE}}` : タイトル
- `{{TABS}}` : タブ部分
- `{{PANELS}}` : 各Markdownの本文
