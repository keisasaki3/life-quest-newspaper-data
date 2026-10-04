# 開発ガイド（Claude / GPT 共通）

このリポジトリを触るAIと人は最初にこれを読む（2026-10-04 Keita依頼）。人生クエスト本体とプロジェクト共通のルールは `keisasaki3/keisasaki3.github.io` の `AGENTS.md`。

## 役割

- 人生クエストの NEWSPAPER（下タブ「ニュース」）が読む公開JSONの置き場。アプリは `newspaper/latest.json` → その `path` の日付JSONを raw.githubusercontent.com から読む。
- `index.html` / `app.js` / `styles.css` は確認用の簡易ビュー（Renderが `main` を自動公開）。人生クエスト本体の画面ではない。

## 毎朝の生成

- ClaudeのroutineがJST 5:20に `GENERATE.md` どおりに作り、`scripts/validate_issue.py` を通してから `main` へPRでマージする。公開の目安は6:15。
- **毎回 `main` の最新の `GENERATE.md` と `STYLE.md` を読み直してから作る。** 手順や書き方は他の作業で変わる（2026-10-04の号は古い書き方で出てしまい、直しのPRが要った）。
- 同じ日の号を並行して発行しない。`newspaper/DATE.json` が既に `main` にあれば何もしない。
- DAILY CULTURE / DAILY QUIZ は2026-10-03から生成停止中（`GENERATE.md` §3・§4）。Keitaの指示があるまで戻さない。

## 変更するとき

- 紙面JSONの形（キー・型）を変えるときは、人生クエストの `apps/life-quest/newspaper-ui.js` と SPEC §14、ここの `validate_issue.py`・`GENERATE.md`・`README.md` を揃えて変える。古い号（項目が無い号）もアプリで表示できるようにしておく。
- 公開済みの号の修正は、修正PRを `main` にマージする（`latest.json` は最後に・同じマージで）。
- 「実装」と言われるまで作らない、指定外を変えない、PRは検証後に自分でマージ、本番表示の確認はKeita、などの共通ルールは本体リポジトリの `AGENTS.md` に従う。
- APIキーやトークンを書かない。
