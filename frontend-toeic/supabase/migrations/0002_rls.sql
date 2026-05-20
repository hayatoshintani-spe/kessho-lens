-- =====================================================================
-- Row Level Security policies
-- =====================================================================

-- Helper: is the caller an admin?
create or replace function public.is_admin()
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select coalesce(
    (select role = 'admin' from public.user_profiles where id = auth.uid()),
    false
  );
$$;

-- ---------- enable RLS ----------
alter table public.skills                    enable row level security;
alter table public.user_profiles             enable row level security;
alter table public.vocabulary_items          enable row level security;
alter table public.quiz_questions            enable row level security;
alter table public.content_items             enable row level security;
alter table public.daily_tasks               enable row level security;
alter table public.learning_sessions         enable row level security;
alter table public.user_vocabulary_reviews   enable row level security;
alter table public.quiz_attempts             enable row level security;
alter table public.shadowing_attempts        enable row level security;
alter table public.speaking_attempts         enable row level security;
alter table public.reading_attempts          enable row level security;
alter table public.weekly_reviews            enable row level security;

-- ---------- master tables: read for all authenticated; write for admin only ----------
do $$
declare t text;
begin
  foreach t in array array['skills','vocabulary_items','quiz_questions','content_items'] loop
    execute format('drop policy if exists "%1$s_select" on public.%1$s', t);
    execute format('drop policy if exists "%1$s_admin_write" on public.%1$s', t);
    execute format(
      'create policy "%1$s_select" on public.%1$s
         for select to authenticated using (true)',
      t
    );
    execute format(
      'create policy "%1$s_admin_write" on public.%1$s
         for all to authenticated using (public.is_admin()) with check (public.is_admin())',
      t
    );
  end loop;
end$$;

-- ---------- user_profiles: own row ----------
drop policy if exists "user_profiles_select_own" on public.user_profiles;
drop policy if exists "user_profiles_insert_own" on public.user_profiles;
drop policy if exists "user_profiles_update_own" on public.user_profiles;
drop policy if exists "user_profiles_delete_own" on public.user_profiles;

create policy "user_profiles_select_own" on public.user_profiles
  for select to authenticated using (id = auth.uid());
create policy "user_profiles_insert_own" on public.user_profiles
  for insert to authenticated with check (id = auth.uid());
create policy "user_profiles_update_own" on public.user_profiles
  for update to authenticated using (id = auth.uid()) with check (id = auth.uid());
create policy "user_profiles_delete_own" on public.user_profiles
  for delete to authenticated using (id = auth.uid());

-- ---------- per-user tables ----------
do $$
declare t text;
begin
  foreach t in array array[
    'daily_tasks','learning_sessions','user_vocabulary_reviews',
    'quiz_attempts','shadowing_attempts','speaking_attempts',
    'reading_attempts','weekly_reviews'
  ] loop
    execute format('drop policy if exists "%1$s_select_own" on public.%1$s', t);
    execute format('drop policy if exists "%1$s_insert_own" on public.%1$s', t);
    execute format('drop policy if exists "%1$s_update_own" on public.%1$s', t);
    execute format('drop policy if exists "%1$s_delete_own" on public.%1$s', t);

    execute format(
      'create policy "%1$s_select_own" on public.%1$s
         for select to authenticated using (user_id = auth.uid())', t);
    execute format(
      'create policy "%1$s_insert_own" on public.%1$s
         for insert to authenticated with check (user_id = auth.uid())', t);
    execute format(
      'create policy "%1$s_update_own" on public.%1$s
         for update to authenticated using (user_id = auth.uid()) with check (user_id = auth.uid())', t);
    execute format(
      'create policy "%1$s_delete_own" on public.%1$s
         for delete to authenticated using (user_id = auth.uid())', t);
  end loop;
end$$;

-- ---------- Storage bucket for recordings ----------
-- Create the bucket in the Supabase dashboard (private) named 'recordings'.
-- Then apply the following storage policies:
--
-- create policy "recordings_select_own" on storage.objects for select to authenticated
--   using (bucket_id = 'recordings' and (storage.foldername(name))[1] = auth.uid()::text);
-- create policy "recordings_insert_own" on storage.objects for insert to authenticated
--   with check (bucket_id = 'recordings' and (storage.foldername(name))[1] = auth.uid()::text);
-- create policy "recordings_delete_own" on storage.objects for delete to authenticated
--   using (bucket_id = 'recordings' and (storage.foldername(name))[1] = auth.uid()::text);
