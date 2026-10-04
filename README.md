# Life Quest Newspaper Data

人生クエスト `NEWSPAPER` 用の公開データ＋簡易ビュー。

作業ルールは [AGENTS.md](AGENTS.md)。

## Viewer

- https://life-quest-newspaper.onrender.com

このビューは確認用。人生クエスト本体はJSONを直接読み込む。

## Endpoints

- Latest pointer: `https://raw.githubusercontent.com/keisasaki3/life-quest-newspaper-data/main/newspaper/latest.json`
- Daily issue: `https://raw.githubusercontent.com/keisasaki3/life-quest-newspaper-data/main/newspaper/YYYY-MM-DD.json`
- Culture registry: `https://raw.githubusercontent.com/keisasaki3/life-quest-newspaper-data/main/registry/culture.json`
- Quiz registry: `https://raw.githubusercontent.com/keisasaki3/life-quest-newspaper-data/main/registry/quiz.json`

## Publish flow

1. Generate and verify the daily issue. Claude does this every morning by [GENERATE.md](GENERATE.md); NEWS follows [STYLE.md](STYLE.md). Check with `python3 scripts/validate_issue.py YYYY-MM-DD`.
2. Write `newspaper/YYYY-MM-DD.json`.
3. Update `registry/culture.json`.
4. Update `registry/quiz.json`.
5. Update `newspaper/latest.json` last, and publish all of the above in one merge to `main`.

`latest.json` is a small pointer. The app/viewer reads the pointer and then fetches the referenced daily issue so a partially generated issue cannot become the published latest edition.

## Viewer files

- `index.html`
- `styles.css`
- `app.js`

Render automatically deploys `main` as a static site.

## Daily issue schema

Top-level fields:

- `schemaVersion`
- `date`
- `timezone`
- `generated_at`
- `news`
- `markets`
- `daily_culture`
- `daily_quiz`

NEWS article fields include `headline_en` / `headline`, sentence-paired English/Japanese summaries, sources, and optional background / why-it-matters. How to write them: [STYLE.md](STYLE.md).

DAILY CULTURE and DAILY QUIZ contain registry metadata used to prevent semantic repetition across past issues.
