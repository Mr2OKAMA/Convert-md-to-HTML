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
| `build.py` | プロパティ＋3つのMarkdown → 目次付きの1ページHTML |
| `templates/procedure.html.j2` | 手順書のHTML構造（Jinja2） |
| `templates/style.css` | 手順書のデザイン・印刷用スタイル |
| `requirements.txt` | 依存ライブラリ（markdown, flask, PyYAML, Jinja2） |

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

既存のタブ表示のデザインは `template.html` で編集できます。次のプレースホルダーが置換されます。

- `{{TITLE}}` : タイトル
- `{{TABS}}` : タブ部分
- `{{PANELS}}` : 各Markdownの本文

## 4要素から手順書を作る

プロパティ・マインドセット・ワークフロー・オペレーションを別ファイルで管理し、`build.py` で1ページにまとめます。

```text
samples/submersible-mixer/
├── 0_property.yaml
├── 1_マインドセット.md
├── 2_ワークフロー.md
├── 3_オペレーション.md
└── index.html              # 生成物（確認用サンプルを同梱）
templates/
├── procedure.html.j2       # HTMLの骨組み
└── style.css               # デザインはここだけで管理
```

`0_property.yaml` には作業名・管理ID・版数・作成者・作成日・承認者と、改訂履歴（版数・日付・改訂者・内容のリスト）を記入します。版数は `"1.0"` のように引用符で囲み、未定の担当者などは空欄にできます。YAMLのコメントはHTMLには出力されません。

リポジトリ直下で実行します。

```sh
pip install -r requirements.txt
python build.py samples/submersible-mixer
python build.py --all
# シェルでフォルダを展開して一括指定する方法
python build.py samples/*
# CSSを埋め込んだ単体HTML（同じindex.htmlを上書き）
python build.py samples/submersible-mixer --inline-css
```

出力先は各フォルダの `index.html` です。フォルダは複数指定でき、一括変換では `0_property.yaml` のないフォルダ（既存の `sludge-collector` など）をメッセージ付きでスキップします。単独指定時のプロパティ不足や、Markdownの不足はエラーになります。

プロパティと改訂履歴、目次、3セクションを表示します。各Markdownの先頭H1はビルド時だけ除去し、タイトルをプロパティから、セクション見出しをテンプレートから付与するため、元のMarkdownは変更しません。表・引用ブロック・`【要確認】` のハイライトに対応し、コード内の `【要確認】` はそのまま表示します。

通常は `templates/style.css` を相対パスで参照するため、**デザイン改定はこのCSSだけを変更**すれば反映されます。配布時はフォルダの相対位置を保ってCSSも渡してください。`--inline-css` の場合はCSS変更後に再ビルドし、生成されたHTMLだけを配布できます（Markdownから参照する画像等は別途必要です）。印刷・PDF保存にも対応しています。

Mermaidコードブロックは図として描画します。Mermaid.jsはバージョンを固定したCDNから取得するため、`--inline-css` 使用時も図の表示にはインターネット接続が必要です。印刷は図が表示されてから行ってください。

既存の `convert.py`・`app.py` は、任意のMarkdownをタブ表示にする従来の用途として引き続き利用できます。`build.py` は `convert.py` のMarkdown変換設定を共用し、手順書専用の組み立て・装飾を追加しています。ルートの `index.html`（静的変換ページ）も変更しません。

入力は管理者が確認した信頼できるローカルファイルを使用してください。Markdown内のHTMLはそのまま出力されるため、未確認の第三者ファイルを公開用HTMLに変換する用途には使用しないでください。
