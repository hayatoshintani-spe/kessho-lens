-- =====================================================================
-- TOEIC Learning App — Initial schema
-- Run this in the Supabase SQL editor (or `supabase db push`).
-- =====================================================================

create extension if not exists "pgcrypto";

-- ---------- helpers ----------
create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

-- ---------- skills (master) ----------
create table if not exists public.skills (
  id uuid primary key default gen_random_uuid(),
  code text unique not null,
  name text not null,
  default_ratio numeric not null default 0,
  icon text,
  sort_order int not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create trigger trg_skills_updated_at before update on public.skills
  for each row execute function public.set_updated_at();

insert into public.skills (code, name, default_ratio, sort_order) values
  ('vocabulary', '単語',         0.25, 1),
  ('grammar',    '文法',         0.15, 2),
  ('listening',  'リスニング',    0.25, 3),
  ('shadowing',  'シャドーイング',0.15, 4),
  ('reading',    '英読',         0.15, 5),
  ('speaking',   'スピーキング',  0.05, 6)
on conflict (code) do nothing;

-- ---------- user_profiles ----------
create table if not exists public.user_profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  display_name text,
  current_toeic int check (current_toeic between 0 and 990),
  target_toeic  int check (target_toeic  between 0 and 990),
  target_date   date,
  daily_minutes int not null default 60 check (daily_minutes between 5 and 480),
  weak_areas    text[] not null default '{}',
  timezone      text not null default 'Asia/Tokyo',
  streak_count  int not null default 0,
  last_studied_on date,
  role text not null default 'user' check (role in ('user', 'admin')),
  onboarded_at  timestamptz,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);
create trigger trg_user_profiles_updated_at before update on public.user_profiles
  for each row execute function public.set_updated_at();

-- Auto-create profile when a new auth user is created.
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.user_profiles (id, display_name)
  values (new.id, split_part(new.email, '@', 1))
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- ---------- vocabulary master ----------
create table if not exists public.vocabulary_items (
  id uuid primary key default gen_random_uuid(),
  word text not null,
  meaning text not null,
  part_of_speech text,
  example_en text,
  example_ja text,
  difficulty int not null default 3 check (difficulty between 1 and 5),
  tags text[] not null default '{}',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create trigger trg_vocabulary_items_updated_at before update on public.vocabulary_items
  for each row execute function public.set_updated_at();
create index if not exists idx_vocabulary_items_difficulty on public.vocabulary_items(difficulty);

-- ---------- quiz questions (grammar / listening / reading) ----------
create table if not exists public.quiz_questions (
  id uuid primary key default gen_random_uuid(),
  skill_code text not null references public.skills(code),
  prompt text not null,
  choices jsonb not null,
  answer_index int not null check (answer_index >= 0),
  explanation text,
  difficulty int not null default 3 check (difficulty between 1 and 5),
  audio_path text,
  passage text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create trigger trg_quiz_questions_updated_at before update on public.quiz_questions
  for each row execute function public.set_updated_at();
create index if not exists idx_quiz_questions_skill on public.quiz_questions(skill_code);

-- ---------- generic content (shadowing prompts, reading passages, etc.) ----------
create table if not exists public.content_items (
  id uuid primary key default gen_random_uuid(),
  skill_code text not null references public.skills(code),
  title text not null,
  body jsonb not null default '{}'::jsonb,
  difficulty int not null default 3 check (difficulty between 1 and 5),
  audio_path text,
  est_minutes int not null default 5,
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create trigger trg_content_items_updated_at before update on public.content_items
  for each row execute function public.set_updated_at();
create index if not exists idx_content_items_skill on public.content_items(skill_code);

-- ---------- daily tasks ----------
create table if not exists public.daily_tasks (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  task_date date not null,
  skill_code text not null references public.skills(code),
  target_minutes int not null check (target_minutes > 0),
  status text not null default 'pending' check (status in ('pending','in_progress','done','skipped')),
  content_item_id uuid references public.content_items(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create trigger trg_daily_tasks_updated_at before update on public.daily_tasks
  for each row execute function public.set_updated_at();
create unique index if not exists uq_daily_tasks_user_date_skill
  on public.daily_tasks(user_id, task_date, skill_code);
create index if not exists idx_daily_tasks_user_date on public.daily_tasks(user_id, task_date);

-- ---------- learning sessions ----------
create table if not exists public.learning_sessions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  skill_code text not null references public.skills(code),
  started_at timestamptz not null default now(),
  ended_at timestamptz,
  duration_seconds int not null default 0 check (duration_seconds >= 0),
  item_count int not null default 0,
  correct_count int not null default 0,
  accuracy numeric,
  difficulty_avg numeric,
  note text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create trigger trg_learning_sessions_updated_at before update on public.learning_sessions
  for each row execute function public.set_updated_at();
create index if not exists idx_learning_sessions_user on public.learning_sessions(user_id, started_at desc);

-- ---------- vocabulary reviews (SM-2 light) ----------
create table if not exists public.user_vocabulary_reviews (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  vocabulary_item_id uuid not null references public.vocabulary_items(id) on delete cascade,
  rating text not null check (rating in ('known','forgot','hard')),
  interval_days int not null default 1,
  next_review_on date not null,
  last_reviewed_at timestamptz not null default now(),
  repetition int not null default 0,
  ease numeric not null default 2.5,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create trigger trg_user_vocabulary_reviews_updated_at before update on public.user_vocabulary_reviews
  for each row execute function public.set_updated_at();
create unique index if not exists uq_user_vocab_review
  on public.user_vocabulary_reviews(user_id, vocabulary_item_id);
create index if not exists idx_user_vocab_next_review
  on public.user_vocabulary_reviews(user_id, next_review_on);

-- ---------- quiz attempts ----------
create table if not exists public.quiz_attempts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  quiz_question_id uuid not null references public.quiz_questions(id) on delete cascade,
  session_id uuid references public.learning_sessions(id) on delete set null,
  selected_index int not null,
  is_correct boolean not null,
  elapsed_seconds int not null default 0,
  created_at timestamptz not null default now()
);
create index if not exists idx_quiz_attempts_user on public.quiz_attempts(user_id, created_at desc);

-- ---------- shadowing attempts ----------
create table if not exists public.shadowing_attempts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  session_id uuid references public.learning_sessions(id) on delete set null,
  content_item_id uuid references public.content_items(id) on delete set null,
  recording_path text,
  self_rating int not null default 3 check (self_rating between 1 and 5),
  note text,
  created_at timestamptz not null default now()
);
create index if not exists idx_shadowing_attempts_user on public.shadowing_attempts(user_id, created_at desc);

-- ---------- speaking attempts ----------
create table if not exists public.speaking_attempts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  session_id uuid references public.learning_sessions(id) on delete set null,
  prompt text not null,
  recording_path text,
  self_rating int not null default 3 check (self_rating between 1 and 5),
  note text,
  created_at timestamptz not null default now()
);
create index if not exists idx_speaking_attempts_user on public.speaking_attempts(user_id, created_at desc);

-- ---------- reading attempts ----------
create table if not exists public.reading_attempts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  session_id uuid references public.learning_sessions(id) on delete set null,
  content_item_id uuid references public.content_items(id) on delete set null,
  read_seconds int not null default 0,
  word_count int not null default 0,
  wpm int not null default 0,
  comprehension int not null default 3 check (comprehension between 1 and 5),
  created_at timestamptz not null default now()
);
create index if not exists idx_reading_attempts_user on public.reading_attempts(user_id, created_at desc);

-- ---------- weekly reviews ----------
create table if not exists public.weekly_reviews (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  week_start date not null,
  total_minutes int not null default 0,
  by_skill jsonb not null default '{}'::jsonb,
  weakest_skill text references public.skills(code),
  top_skill text references public.skills(code),
  focus_next_week text[] not null default '{}',
  note text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create trigger trg_weekly_reviews_updated_at before update on public.weekly_reviews
  for each row execute function public.set_updated_at();
create unique index if not exists uq_weekly_reviews_user_week
  on public.weekly_reviews(user_id, week_start);
