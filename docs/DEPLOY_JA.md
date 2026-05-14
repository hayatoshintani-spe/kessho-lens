# 📱 デプロイ手順（スマホ・初心者向け）

このアプリをインターネットに公開して、URLで誰でも見られる状態にする手順です。

**所要時間: 約7分**  
**費用: 無料**  
**必要なもの: GitHub アカウントだけ**

---

## 全体の流れ

```
①ヒミツの合言葉を作る  →  ②裏方を Render に置く  →  ③表側を Vercel に置く  →  ④2つをつなぐ
```

---

## ① ヒミツの合言葉を作る（30秒）

このあと2回、同じ文字列を貼り付けます。何でもいい英数字を決めてメモしてください。

例:
```
mySecret2026abcXYZ
```

そのまま使ってOK。長くて推測しにくいほど安全。

---

## ② 裏方プログラムを Render に置く（3分）

裏方 = データ計算をする部分（FastAPI）

### 2-1. このリンクを開く

👉 **https://render.com/deploy?repo=https://github.com/hayatoshintani-spe/kessho-lens**

### 2-2. Render にログイン

「Sign in with GitHub」ボタン → GitHub のパスワード → 「Authorize Render」

### 2-3. Blueprint の画面で

- **Blueprint Name**: `kessho-lens` のまま OK
- **Branch**: `claude/setup-production-deployment-BZIbe` を選択

### 2-4. 「Environment Variables」の欄に貼り付け

以下を入力:

| 名前 | 値 |
|---|---|
| `CRON_SECRET` | ①で決めた合言葉（例: `mySecret2026abcXYZ`） |
| `ANTHROPIC_API_KEY` | （あれば）`sk-ant-...` 持ってなければ空のままでOK |

### 2-5. 「Apply」をタップ

数分待つと「Live」と表示されます。

### 2-6. 完成した URL をメモ

画面の上の方に出ている URL をコピーします。

```
例: https://kessho-lens-backend.onrender.com
```

これを **「裏方URL」** と呼びます。

---

## ③ 表側を Vercel に置く（2分）

表側 = 画面を見せる部分（Next.js）

### 3-1. このリンクを開く

👉 **https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fhayatoshintani-spe%2Fkessho-lens&root-directory=frontend**

### 3-2. Vercel にログイン

「Continue with GitHub」 → 「Authorize Vercel」

### 3-3. 「Configure Project」画面で

- **Project Name**: そのままでOK
- **Framework Preset**: `Next.js`（自動）
- **Root Directory**: `frontend`（自動）

### 3-4. 「Environment Variables」を開いて入力

| 名前 | 値 |
|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | ②でメモした「裏方URL」 |
| `CRON_SECRET` | ①で決めた合言葉（②と**同じ**） |

### 3-5. 「Deploy」をタップ

1〜2分待つと完成。「Visit」をタップすると **これが公開URL** です。

```
例: https://kessho-lens.vercel.app
```

これを **「表側URL」** と呼びます。

🎉 **この時点でブラウザから見られます！**

---

## ④ 2つをつなぐ（1分・最後の仕上げ）

CORS という仕組みで、裏方が「表側からのアクセスだけ許可」する設定をします。これをやらないとデータが表示されないことがあります。

### 4-1. Render のダッシュボードを開く

https://dashboard.render.com → `kessho-lens-backend` をタップ

### 4-2. 左メニューの「Environment」をタップ

### 4-3. 「Add Environment Variable」をタップ

| 名前 | 値 |
|---|---|
| `FRONTEND_URL` | ③でメモした「表側URL」 |

### 4-4. 「Save Changes」

裏方が自動で再起動します（2〜3分）。

---

## ✅ 完了確認

「表側URL」をブラウザで開いて:

- ダッシュボードに4体のAIエージェントが表示される
- グラフが描画される
- 「会議ログ」をタップすると過去の議論が読める
- 「日次レポート」が日本語で表示される

これが表示されればすべて成功 🎉

---

## ❓ うまく動かない時

### ダッシュボードは出るけどデータが「デモモード」表示

→ ④の手順をやり直す（FRONTEND_URL が間違っている可能性）

### Vercel で「Build failed」

→ Vercel のダッシュボードでログを確認。たいてい Root Directory が `frontend` になっていない

### Render で「Build failed」

→ Render のダッシュボードでログを確認。Python のバージョンミスマッチが多い

### 「Application error」と画面に出る

→ 環境変数を確認。「裏方URL」をコピペした時に `https://` が抜けていないか

困ったら、エラーメッセージのスクショと一緒にチャットで連絡してください。
