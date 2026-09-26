# Life Quest Newspaper Data

人生クエスト `NEWSPAPER` タブ用の公開データリポジトリ。

## Endpoints

- Latest pointer: `https://raw.githubusercontent.com/keisasaki3/life-quest-newspaper-data/main/newspaper/latest.json`
- Daily issue: `https://raw.githubusercontent.com/keisasaki3/life-quest-newspaper-data/main/newspaper/YYYY-MM-DD.json`
- Culture registry: `https://raw.githubusercontent.com/keisasaki3/life-quest-newspaper-data/main/registry/culture.json`
- Quiz registry: `https://raw.githubusercontent.com/keisasaki3/life-quest-newspaper-data/main/registry/quiz.json`

## Publish flow

1. Generate and verify the daily issue.
2. Write `newspaper/YYYY-MM-DD.json`.
3. Update `registry/culture.json`.
4. Update `registry/quiz.json`.
5. Update `newspaper/latest.json` last.

`latest.json` is intentionally a small pointer. The app reads the pointer and then fetches the referenced daily issue. This prevents a partially generated issue from becoming the published latest edition.

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

NEWS article fields include sentence-paired Japanese/English summaries, background, why-it-matters, and sources.

DAILY CULTURE and DAILY QUIZ contain registry metadata used to prevent semantic repetition across past issues.
