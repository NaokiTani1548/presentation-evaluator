# presentation-evaluator

プレゼンテーションのスライド（PDF）と音声ファイルをアップロードすることで、構成・話速・知識レベル・ペルソナ別フィードバック・前回との比較など多角的な自動評価を行う FastAPI ベースの Web API

---

## 機能概要

- スライドの評価
- 音声ファイルからの自動文字起こし
- 発表構成の自動評価
- 話速の自動評価
- 前提知識レベル評価
- ペルソナ別フィードバック
- 前回発表との比較評価

## ex

- スライド自動修正
- AI 音声での適切な発表スピード

---

## ディレクトリ構成

```
presentation-evaluator/
├── backend/
│   ├── main.py
│   ├── services/
│   │   ├── slide_parser.py
│   │   └── transcribe.py
│   ├── agents/
│   │   ├── structure.py
│   │   ├── speech_rate.py
│   │   ├── prior_knowledge.py
│   │   ├── persona.py
│   │   └── comparison.py
│   ├── sample/
│   │   ├── slide_sample.pdf
│   │   └── transcript_sample.txt
│   ├── db/
│   └── requirements.txt
├── .env
└── README.md
```

---

## セットアップ

```bash
$ git clone git@github.com:NaokiTani1548/presentation-evaluator.git
$ cd presentation-evaluator
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r backend/requirements.txt
```

### 依存パッケージのインストール\*\*

```bash
$ pip install -r backend/requirements.txt
```

### 共有用依存ファイル更新

```bash
$ pip freeze > backend/requirements.txt
```

## サーバーの起動

```bash
uvicorn backend.main:app --reload
```

## API エンドポイント

### `/evaluate/` (POST)

- **説明**: スライド（PDF）と音声ファイル（例: 発表音声）、前回の発表原稿（任意）を受け取り、各種評価結果を返す。
- **パラメータ**:

  - `slide`: PDF ファイル
  - `audio`: 音声ファイル（例: wav, mp3）
  - `prev_transcript`: 前回発表の原稿（？）

- **レスポンス例**:
  ```json
  {
    "slide_text": "...",
    "transcript": "...",
    "structure": "...",
    "speech_rate": "...",
    "prior_knowledge": "...",
    "persona_feedback": "...",
    "comparison": "..."
  }
  ```

---

# git を用いた開発手順

## 初期セットアップ

```bash
$ git clone <リポジトリのURL>
```

## 機能開発手順

0. リモートの最新を取得

```bash
$ git pull
```

1. 機能単位でブランチを切る

```bash
$ git switch -c <新しいブランチ名>
```

2. コード変更時（commit は履歴に残るので、定期的に実行することをお勧めします）

```bash
$ git add .  (.　もしくはファイル名指定)
$ git commit -m '<コミットメッセージ（できるだけ詳しく）>'
```

3. 機能実装完了時

```bash
$ git push
```

## コンフリクト発生時

### main ブランチ

```bash
$ git switch main
$ git pull
```

### コンフリクトが起きたブランチ

```bash
$ git switch <作業ブランチ>
$ git rebase main
```

以下 URL の手順(6)移行を参照
https://qiita.com/C_HERO/items/06669621a1eb12d8799e

## ブランチ切り替え

```bash
$ git switch <切り替え先ブランチ名>
```
