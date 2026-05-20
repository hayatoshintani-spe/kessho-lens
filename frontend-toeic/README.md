# Kessho Lens English — TOEIC 学習管理アプリ (MVP)

TOEIC 500 → 900 を目指す学習者向けの、毎日の学習を可視化する学習管理 Web アプリ。

- Next.js 14 (App Router) + TypeScript
- Tailwind CSS + 自前 shadcn/ui プリミティブ
- Supabase (Auth / PostgreSQL / Storage)
- Vercel デプロイ想定

このディレクトリは既存の `kessho-lens` リポジトリの中に独立した形で配置されています（既存の `frontend/` / `backend/` には触れません）。

## セットアップ

### 1. 依存をインストール

```bash
cd frontend-toeic
npm install
```

### 2. Supabase プロジェクトを用意

1. [https://supabase.com/](https://supabase.com/) で新規プロジェクトを作成。
2. SQL Editor で **`supabase/migrations/0001_init.sql`** → **`supabase/migrations/0002_rls.sql`** → **`supabase/seed.sql`** の順で実行。
3. Storage で **`recordings`** という名前の **非公開バケット** を作成。
4. Storage Policy として、`0002_rls.sql` の末尾に書かれている 3 つの policy を SQL Editor で実行。

### 3. 環境変数

```bash
cp .env.local.example .env.local
```

`.env.local` に以下を設定:

| 変数 | 用途 |
|---|---|
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase Project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | anon public key |
| `SUPABASE_SERVICE_ROLE_KEY` | server-only (RLS bypass を使う API がある場合のみ。MVPでは未使用) |
| `NEXT_PUBLIC_APP_URL` | デフォルト `http://localhost:3000` |

### 4. 起動

```bash
npm run dev
```

→ http://localhost:3000

## ファイル構成

```
frontend-toeic/
├── app/
│   ├── (public)/
│   │   ├── page.tsx              # ランディング /
│   │   └── login/page.tsx        # /login
│   ├── (app)/                    # 認証必須
│   │   ├── layout.tsx
│   │   ├── onboarding/
│   │   ├── dashboard/
│   │   ├── study/{vocabulary,grammar,listening,shadowing,reading,speaking}/
│   │   ├── logs/
│   │   ├── review/weekly/
│   │   └── admin/
│   └── api/tasks/generate/route.ts
├── components/{ui,layout,dashboard,study}/
├── lib/{supabase,tasks,audio,utils,types,study}/
├── supabase/migrations/*.sql
├── supabase/seed.sql
└── middleware.ts                 # セッション更新 + redirect
```

## DB スキーマ概要

| テーブル | 用途 |
|---|---|
| `skills` | スキル定義 (master) |
| `user_profiles` | オンボーディング情報 / streak |
| `vocabulary_items` | 単語マスタ |
| `quiz_questions` | 4択問題 (grammar / listening / reading) |
| `content_items` | 汎用教材 (shadowing/reading/speaking/listening) |
| `daily_tasks` | 日次タスク |
| `learning_sessions` | 学習セッション (集約) |
| `user_vocabulary_reviews` | SM-2 ライト復習スケジュール |
| `quiz_attempts` | 4択問題の解答記録 |
| `shadowing_attempts` / `speaking_attempts` / `reading_attempts` | 各スキルの個別記録 |
| `weekly_reviews` | 週次レビュー (MVP では計算で動的生成) |

RLS は全テーブルで有効化済み。**ユーザーは自分のデータだけを読み書き可能**。マスタテーブル (`skills`, `vocabulary_items`, `quiz_questions`, `content_items`) は `SELECT` が全認証ユーザーに許可されており、`INSERT/UPDATE/DELETE` は `user_profiles.role = 'admin'` のみ可能。

## 学習タスク生成ロジック

`lib/tasks/generateDailyTasks.ts` にロジックがあります。

- ベース比率: 単語 25% / 文法 15% / リスニング 25% / シャドーイング 15% / 英読 15% / スピーキング 5%
- 苦手分野 (`user_profiles.weak_areas`) は +5% され、他から自動で按分
- 5分単位に丸め、最小 5分

## 動作確認の流れ

1. `/` → 「はじめる」 → `/login` → 新規登録（メール＋パスワード）。
   - Supabase の **Auth** で「Confirm email」をオフにすると即座にログインできます（推奨：MVP動作確認時のみ）。
2. `/onboarding` で目標と1日の時間、苦手分野を入力。
3. `/dashboard` で「今日のタスクを生成」を押す → 6 つの skill 別タスクが表示される。
4. 各 `/study/*` でセッションを実施 → 終了で `learning_sessions` に記録 + 当日タスクが done に。
5. `/logs` で履歴、`/review/weekly` で週次サマリ。
6. `/admin` で教材を追加（`user_profiles.role = 'admin'` のユーザーのみ書き込み可）。

## 次にやるべきこと（MVP 後）

- [ ] PWA 化 (オフライン対応 + ホーム画面追加)
- [ ] リスニング/シャドーイング教材に **音声ファイル** を Supabase Storage 経由で配信
- [ ] 録音の AI 採点 (発音 / 流暢さ)
- [ ] スコア予測モデル (学習履歴 → 推定 TOEIC)
- [ ] 復習キューを `/study/vocabulary` だけでなく他スキルにも拡張
- [ ] テスト (`vitest` + `@testing-library/react`)
- [ ] E2E (`Playwright`)
- [ ] CI (GitHub Actions: type-check / lint)

## デプロイ (Vercel)

1. Vercel に GitHub リポジトリを接続。
2. Root Directory を `frontend-toeic` に設定。
3. Build Command: `npm run build` / Output: `.next`
4. Environment Variables に `.env.local` と同じものを設定。
