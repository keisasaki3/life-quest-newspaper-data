# 毎朝の生成手順（Claude）

人生クエスト NEWSPAPER の1日分を作って公開する手順。毎朝 Claude の routine がこの通りに動く（2026-09-27 に ChatGPT から移行）。人が手で作るときも同じ手順でよい。

`DATE` は日本時間の今日（`TZ=Asia/Tokyo date +%F`）。

## 0. 準備

- `STYLE.md`、`newspaper/latest.json`、直近2日分の `newspaper/*.json` を読む。
- `newspaper/DATE.json` がもう `main` にあれば、何もせず終わる（二重発行しない）。

## 道具

- 市場データ：`python3 scripts/fetch_markets.py` が MARKETS の数値（Yahoo Finance、株探のTOPIX、米財務省、財務省の国債金利）をまとめて出す。`missing` に出たものは手で確かめるか外す。
- 記事本文：`python3 scripts/fetch_text.py URL`、見出し一覧：`python3 scripts/fetch_text.py --rss URL`。WebFetch は開けないサイトが多いので、こちらを使う。
- 見出し集め：BBC（`https://feeds.bbci.co.uk/news/world/rss.xml`、`/business/`、`/technology/`）、The Japan Times（`https://www.japantimes.co.jp/feed/`）、Google News（`https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en`、日本語は `hl=ja&gl=JP&ceid=JP:ja`）。Google News のリンクは開けないので、見つけた記事は発行元のサイトで探して開く。WebSearch も使ってよい。
- Reuters・AP・Bloomberg・NYT・WSJ・FT・朝日・毎日などはボット対策で本文を開けない。BBC、The Guardian、Al Jazeera、NPR、CNN、DW、The Japan Times、Nikkei Asia、共同（英語）、NHK WORLD、時事、読売、tenki.jp、官公庁のサイトは開ける。開けない出典は `sources` に使わない。

## 1. NEWS（5本前後）

- 対象は日本時間で前日朝〜今朝のニュース。世界・日本・米国を中心に、大事な順に5本前後。
- Web検索で候補を集め、記事本文を開いて事実を確かめる。見出しや検索結果の要約だけで書かない。
- 出典は本文を開いて確かめた記事だけ。一次に近いもの（政府・中央銀行・気象庁など）や大手の報道を優先。`sources[0]` に主な出典を1つ。
- 前日の号と同じ話題は、新しい展開があるときだけ。
- 書き方は `STYLE.md` のとおり（英日両方、ひとこと見出し、事実→最後の文が解説、出典）。日本語は英語を意訳せず、単語のニュアンスを残して訳す。日本の記事は `region: "japan"`（アプリが🇯🇵を付ける）。
- `background` / `why_it_matters` は任意。書くなら日本語で1〜2文。

## 2. MARKETS

これまでの号と同じ形・同じ銘柄にする（勝手に増減しない）。

| グループ | 銘柄 |
|---|---|
| `fx` | USD/JPY、EUR/JPY、EUR/USD |
| `stocks` | NIKKEI225、TOPIX、S&P500、NASDAQ、DOW |
| `rates` | JP10Y、US2Y、US10Y（`unit: "%"`、変化は `change_bp`） |
| `commodities` | GOLD（`USD/oz`）、WTI（`USD/bbl`） |
| `crypto` | BITCOIN（`USD`） |

- 各項目は `symbol` / `value`（数値）/ `change_pct` か `change_bp` / `source` / `source_url`。`change_pct` の項目には値幅 `change`（前日終値からの差、`value` と同じ桁。例 日経 `-647.26`）も入れる（`fetch_markets.py` が出す。手で埋めるときは `value - 前日終値`）。
- 値は最新の確定終値（米国は前日の引け）。数字は出典ページで確かめたものだけ。取れなかった銘柄は推測で埋めず、その項目を外して `as_of` に書く。
- `as_of` にいつ時点のデータかを英語1文で書く。
- `market_moves` は大きく動いた2〜3銘柄について `{symbol, move, explanation}`。`explanation` は日本語で、報道で確かめられる理由だけ。断定できないときはそう書く。

## 3. DAILY CULTURE（2026-10-03 から生成停止中。再開するときだけ以下に従う）

停止中は `daily_culture` を紙面JSONに入れず、`registry/culture.json` も更新しない。再開するときは5のファイルに `daily_culture` と registry 追記を戻す。

- 1日1本の読み物（日本語で600〜900字程度、これまでの号と同じくらい。段落は `\n\n`）。「へえ」となる具体的な事実から入り、最後に物の見方が1つ変わるように締める。
- `registry/culture.json` の過去の `topic_key` と同じ題材は使わない。`angle_key` や `entities` が近いものも避ける。
- 形：`{title, body, explore: [3〜5語], sources: [{name, url}]}`。事実は出典で確かめる。

## 4. DAILY QUIZ（2026-10-03 から生成停止中。再開するときだけ以下に従う）

停止中は `daily_quiz` を紙面JSONに入れず、`registry/quiz.json` も更新しない。再開するときは5のファイルに `daily_quiz` と registry 追記を戻す。

- 1問1答（選択肢なし）。答えが1つに決まる問題。
- `registry/quiz.json` の過去の `fact_key` と同じ事実は使わない。直前数日とジャンルが続かないようにする。
- 形：`{genre, question, answer, explanation, sources}`。

## 5. ファイルを書く

1. `newspaper/DATE.json`：`{schemaVersion: 1, date: DATE, timezone: "Asia/Tokyo", generated_at: "<今の時刻 +09:00>", news, markets}`（停止中は `daily_culture` / `daily_quiz` を入れない。再開時は末尾に足す）
2. （再開時のみ）`registry/culture.json` の `items` の末尾に `{date, title, topic_key, angle_key, entities, knowledge_claims}` を追加
3. （再開時のみ）`registry/quiz.json` の `items` の末尾に `{date, genre, question, answer, fact_key, answer_key, entities}` を追加
4. `newspaper/latest.json` を `{schemaVersion: 1, date: DATE, path: "newspaper/DATE.json", published_at: "<今の時刻 +09:00>"}` に更新

JSON は UTF-8、2スペースインデント、日本語はエスケープしない。再開時の registry への追加は `python3 scripts/registry_add.py culture|quiz ENTRY.json` を使う（同じ日付があれば置き換え、書き方は既存のまま）。

## 6. 検証

```sh
python3 scripts/validate_issue.py DATE
```

ERROR が1つでもあれば直してから再実行。WARN は読んで、直せるものは直す。加えて自分で読み直す：英日が同じことを言っているか、事実の文が出典にあるか、解説で新しい事実を作っていないか。

## 7. 公開

- 1つのコミット（`Publish NEWSPAPER issue for DATE`）にまとめ、作業ブランチから `main` へ PR を作り、検証が通っていればそのままマージする。1回のマージで号・registry・`latest.json` が同時に入るので、途中状態が公開されることはない。
- 公開の目安は日本時間 6:15。
- マージ後、`https://raw.githubusercontent.com/keisasaki3/life-quest-newspaper-data/main/newspaper/latest.json` が DATE を指していることを確かめる。

## つまずきやすい点

- 5:20 JST 時点では Yahoo の日経平均（`^N225`）が前日のままのことがある。株探（`https://kabutan.jp/stock/?code=0000`）の終値・前日終値で確かめる。
- 米財務省のCSVはときどきTLSエラー（curl 35）で落ちる。少し待って取り直す。
- 財務省の `jgbcm.csv` は当月分だけなので、月初の営業日は `fetch_markets.py` が `data/jgbcm_all.csv` に切り替える。
- `market_moves` の理由が読める報道で確かめられないとき（CNBC・Reutersは403になりやすい）は、推測で書かず「理由は確かめられなかった」と書く。

## 失敗したとき

- 途中で失敗したら `main` には何も入れない（前日の号がそのまま表示される）。
- 何ができなかったかを実行結果の最後に書く。
