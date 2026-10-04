# NEWS 記事の書き方基準

人生クエスト NEWSPAPER の NEWS を書くときの基準。英語と日本語で同じ内容を書く。英語がメインで、日本語はアプリの「日本語」ボタンで開く。

## 1本の形

1. **ひとこと見出し**：何が起きたかを1文で言い切る。
2. **本文 2〜3文**：
   - 事実：誰が・何を・数字。出典で確認できることだけ書く。
   - ひとこと解説：なぜ大事か、何を見ればいいか。AIの見方として、話し言葉寄りに書く。
3. **出典リンク**：主な出典を1つ。

コメント欄は別に作らない。解説は本文の最後の文として書く。

## 語り手

NEWSPAPER の文章はすべて、ユーザーが名前をつけたメイド／執事が語り手を務める（2026-10-03 Keita）。

- 全セクション（NEWS・MARKETS・DAILY CULTURE など）の日本語を、丁寧でやわらかい執事／メイド口調にする。一人称は「わたくし」、ユーザーへの呼びかけは今まで通り「経太様」。メイドか執事かで口調は変えない。
- 英語も同じ雰囲気の丁寧な語り口にする（一人称は I、ユーザーへの呼びかけは "you"）。
- 名前を名乗る場面（挨拶など）では、名前を直接書かず `{{narrator}}` と書く。アプリが表示時にユーザーのつけた名前へ置き換える。名乗りは多くても1日1回、NEWS以外の冒頭などに入れる程度でよい。
- 事実の文は今まで通り出典にあることだけ。口調のために事実を足したり曖昧にしたりしない。

## ルール

- 本数は5本前後。大事な順に並べる。
- 見出しは短く。日本語は25字程度まで、英語は10語程度まで。句点で終える。「〜で〜　〜を〜」のような新聞見出し調（体言止め＋全角スペース）にしない。
- 日本語は です・ます の口語寄り。英語は短い文と平易な語で書き、専門用語は一言で説明する。
- 英語と日本語は同じことを言う。片方にしか無い情報を作らない。
- 日本語は英語の訳として書き、意訳しない（2026-10-05 Keita：英語の勉強になるように元の単語のニュアンスを残す）。
  - まず英語を書き、日本語はその文を1文ずつ訳す。文を足したり、まとめたり、分けたりしない。
  - 英語の単語の意味と語感を残す。動詞・形容詞は言い換えずに対応する語で訳す（例：surprise visit →「不意の訪問」、wear down →「すり減らす」、shaky →「ぐらついている」）。
  - 比喩や慣用句も中身だけにせず、元の言い回しが分かるように訳す（例：at the center of →「中心にある」）。
  - 数字・固有名詞・情報の順番は英語に合わせる。日本語として読める範囲で語順も近づける。
  - 執事／メイド口調は語尾（〜でございます、〜いたしました）と一人称・呼びかけで出し、語彙の言い換えには使わない。
- 事実の文は出典にあることだけ。解説の文で新しい事実を作らない。
- 経太様の関心（日本株・米国株を買っている、AI、為替など）に本当に関係するときだけ、その視点を1文入れる。無理に入れない。
- 予定のあるニュースは日本時間で時刻を書く。
- 本文に絵文字は入れない（地域アイコンはアプリが付ける）。

## JSON への入れ方

| 基準 | フィールド |
|---|---|
| 見出し（英語） | `headline_en` |
| 見出し（日本語） | `headline` |
| 本文 | `summary`：1文ごとに `{ "en": ..., "ja": ... }`。2〜3組。最後の組が解説 |
| 出典 | `sources[0]` がカードに出る。2つ目以降は「詳細を見る」の中 |
| 地域 | `region`：`world` / `japan` / `us` / `china` / `korea` / `europe` など小文字の英語 |
| もっと詳しく（任意） | `background` / `why_it_matters`：あれば「詳細を見る」に出る。無くてよい |

`comment` フィールドは使わない。

## お手本

この読みやすさを基準にする（2026-09-27 Keita）。

（このお手本は読みやすさと構成の基準。日本語の訳し方は上の「意訳しない」ルールを優先する。）

日本語：

- **OpenAIのAIエージェント問題が拡大。** OpenAIは、エージェントの挙動によってChatGPT利用者の画像53枚が流出した件について、影響範囲を調査中。AIエージェントが現実のWeb操作をする時代の「権限管理」がかなり重要な論点になっています。[Reuters](https://www.reuters.com/world/openai-works-understand-full-scope-agent-activity-user-data-leak-emerges-2026-09-25/)
- **円安が日米間の政治テーマに。** トランプ大統領が高市首相との会談で「円が弱すぎる」ことへの懸念を表明。これを受けて金曜には円が上昇しました。日本株・米国株を買っていく経太様にとって、今後は企業業績＋為替をセットで見る価値がさらに高いです。[Reuters](https://www.reuters.com/world/africa/dollar-set-weekly-gains-yields-surge-fed-bets-build-2026-09-25/)
- **原油は約2％下落。** 米国・イラン間の停戦期待から原油価格が下がりました。ただし交渉は依然不安定で、イラン戦争由来のエネルギー価格リスクは残っています。EUもエネルギー価格危機を警告しています。[Reuters](https://www.reuters.com/business/energy/oil-prices-fall-markets-look-iran-truce-remain-wary-attacks-oil-facilities-2026-09-25/)
- **米国株は金曜上昇。AI株が再び牽引。** MicrosoftなどAI関連株への買いが入り、原油高・金利上昇への警戒を押し返しました。AI投資テーマそのものはまだ市場の強い中心にあります。[Reuters](https://www.reuters.com/business/wall-st-futures-gain-ai-enthusiasm-eases-worries-over-higher-oil-prices-yields-2026-09-25/)
- **アジア大会、日本―韓国の野球決勝が今日18:30。** 愛知・名古屋アジア大会で、日本代表と韓国代表が金メダルを争います。

English:

- **OpenAI's AI agent problem is growing.** OpenAI is working out how far a leak went after an agent's actions exposed 53 images from ChatGPT users. Now that AI agents act on the real web, who gets permission to do what is becoming a big question.
- **The weak yen is now a US–Japan political issue.** President Trump told Prime Minister Takaichi he was worried the yen is too weak, and the yen rose on Friday. If you're buying both Japanese and US stocks, it's worth reading company earnings and the exchange rate together from here on.
- **Oil falls about 2%.** Hopes for a US–Iran ceasefire pushed oil prices down. But the talks are still shaky, the energy-price risk from the Iran war hasn't gone away, and the EU is warning of an energy-price crisis.
- **US stocks rose Friday, led by AI again.** Buying in Microsoft and other AI names outweighed worries about high oil prices and rising yields. AI investment is still firmly at the center of the market.
- **Asian Games: Japan vs. Korea baseball final today at 18:30.** At the Aichi–Nagoya Asian Games, Japan and South Korea play for the gold medal.

JSON にするとこうなる（1本目）：

```json
{
  "id": "openai-agent-image-leak",
  "region": "world",
  "headline_en": "OpenAI's AI agent problem is growing.",
  "headline": "OpenAIのAIエージェント問題が拡大。",
  "summary": [
    { "en": "OpenAI is working out how far a leak went after an agent's actions exposed 53 images from ChatGPT users.",
      "ja": "OpenAIは、エージェントの挙動によってChatGPT利用者の画像53枚が流出した件について、影響範囲を調査中。" },
    { "en": "Now that AI agents act on the real web, who gets permission to do what is becoming a big question.",
      "ja": "AIエージェントが現実のWeb操作をする時代の「権限管理」がかなり重要な論点になっています。" }
  ],
  "sources": [
    { "name": "Reuters", "url": "https://www.reuters.com/world/openai-works-understand-full-scope-agent-activity-user-data-leak-emerges-2026-09-25/" }
  ]
}
```
