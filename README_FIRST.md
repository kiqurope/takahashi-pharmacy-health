# タカハシ薬局 健康情報・薬膳レシピ（無料公開用サイト）

スマートフォンから見やすい無料公開用の静的ホームページです。

## 含まれるページ

- `docs/index.html` : トップページ
- `docs/health/index.html` : 健康情報一覧
- `docs/health/winter-health-202612.html` : 2026年12月号「冬の感染症に備える、毎日の健康習慣」
- `docs/recipes/index.html` : 薬膳レシピ一覧
- `docs/recipes/kimchi-udon-202611.html` : 2026年11月号「キムチうどん」
- `docs/assets/recipe_20261118.pdf` : 印刷用A4レシピ

## GitHub Pagesで無料公開する方法（初回のみ）

1. GitHubで新規の **公開リポジトリ**（例 `takahashi-pharmacy-health`）を作成します。リポジトリを公開すると、この一式のファイルも原則公開されます。顧客の個人情報や内部資料は入れないでください。
2. このZIPの中身（`content`, `site`, `docs`, `.github`）を、リポジトリのルートへアップロードして `main` にコミットします。GitHubのファイルアップロード画面は、ZIPそのものではなく展開後のファイルを登録してください。`.github/workflows/deploy.yml` は必ず維持します。
3. リポジトリの `Settings → Pages → Build and deployment → Source` で **GitHub Actions** を選択します。
4. `Actions` にある「タカハシ薬局 無料サイト自動更新」を1回実行するか、初回コミットの実行結果を確認します。処理が成功するとサイトの実URLが表示されます。
5. LINEリッチメニューで健康情報のボタンには `https://<GitHubユーザー名>.github.io/<リポジトリ名>/health/`、薬膳レシピには `https://<GitHubユーザー名>.github.io/<リポジトリ名>/recipes/` を設定します。ここに書いたURLは例示であり、実際のページURLはリポジトリから確認してください。

## 毎月の更新について

- 健康情報はChatGPTの既存のLINE月刊投稿案を基に作成し、新しい記事オブジェクトを `content/articles.json` の配列へ追記します。
- 薬膳レシピは毎月第2土曜日の既存タスクから印刷用A4 PDFと料理画像を作り、`content/recipes.json` に新しいレシピオブジェクトを追記します。PDF・画像は `content/assets/` に置きます。
- 既存の `id` は変更せず、二重追加しないでください。各記事には日付 `date` と掲載開始日 `publish_on` (`YYYY-MM-DD`) が必要です。
- 追加内容がGitHubの `main` に反映されると `deploy.yml` が自動でビルドと公開を実行します。毎日 9:18（日本時間）の予備更新も設定してあります（GitHub側の混雑時は遅れる場合があります）。
- 予約原稿を将来の `publish_on` でGitHubに先に登録しておくと、当日以降の日次再構築で表示されます。
- ただし、**ChatGPTライブラリで作成した原稿が自動的にGitHubに転送されるわけではありません**。接続可能なGitHub書き込み操作を使って `content/` にコミットする仕組みが別途必要です。転送・公開までの自動化はGitHub接続後に実地確認してください。
- LINEへの一斉配信は自動では行いません。

## ローカルでのテスト

Python 3.12以降のみを使用します。追加のPythonライブラリは不要です。

```bash
python site/build.py
python -m http.server --directory docs 8000
```

ブラウザで `http://localhost:8000/` を開くと確認できます。

掲載開始日の再現テストは `SITE_DATE=2026-12-01 python site/build.py` のように実行します。

## 注意事項

- GitHub Freeで無料のPages公開は、原則**公開リポジトリ**が対象です。
- GitHubで公開されたファイルは原則全員が閲覧できます。医療情報の根拠は掲載前に再確認してください。
- GitHub Actionsの定期実行は保証された時刻ぴったりではなく、公開リポジトリで60日間リポジトリ活動がなければ定期実行が無効になることがあります。定期的に実行状況を確認してください。
- WordPress等の有料契約は不要です。
