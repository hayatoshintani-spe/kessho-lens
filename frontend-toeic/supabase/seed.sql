-- =====================================================================
-- Original sample content for the TOEIC learning MVP.
-- All sentences below are written from scratch for this app.
-- Run AFTER 0001_init.sql and 0002_rls.sql.
-- =====================================================================

-- ---------- vocabulary ----------
insert into public.vocabulary_items (word, meaning, part_of_speech, example_en, example_ja, difficulty, tags) values
  ('allocate',     '〜を割り当てる',   'verb',  'We will allocate ten minutes to each team.',     '各チームに10分ずつ割り当てます。',         3, '{business}'),
  ('comprehensive','包括的な',         'adj',   'They published a comprehensive report on safety.','彼らは安全に関する包括的な報告書を出した。',3, '{business}'),
  ('deliberate',   '意図的な',         'adj',   'Her silence was deliberate, not accidental.',     '彼女の沈黙は意図的で、偶然ではなかった。',  4, '{general}'),
  ('feasible',     '実現可能な',       'adj',   'The plan is feasible within our budget.',         'その計画は予算内で実現可能です。',          3, '{business}'),
  ('initiate',     '〜を開始する',     'verb',  'We initiated the new training program last week.','先週、新しい研修プログラムを開始しました。',3, '{business}'),
  ('mandatory',    '必須の',           'adj',   'Attendance at the meeting is mandatory.',         '会議への出席は必須です。',                  3, '{business}'),
  ('negotiate',    '〜を交渉する',     'verb',  'We need to negotiate the contract terms again.',  '契約条件をもう一度交渉する必要がある。',    3, '{business}'),
  ('prompt',       '迅速な / 促す',    'adj',   'Thank you for your prompt reply.',                '迅速なご返信ありがとうございます。',        2, '{general}'),
  ('reluctant',    '気が進まない',     'adj',   'She was reluctant to share her draft.',           '彼女は下書きを見せたがらなかった。',        4, '{general}'),
  ('subsequent',   'その後の',         'adj',   'Subsequent meetings will be held online.',        'その後の会議はオンラインで行われます。',    4, '{business}')
on conflict do nothing;

-- ---------- grammar quiz ----------
insert into public.quiz_questions (skill_code, prompt, choices, answer_index, explanation, difficulty) values
  ('grammar',
   'If I ____ more time, I would learn another language.',
   '["have","had","have had","having"]'::jsonb, 1,
   '仮定法過去。現在の事実に反する仮定は If + 過去形, would + 原形。', 3),

  ('grammar',
   'The proposal ____ by the board next Monday.',
   '["reviews","is reviewing","will be reviewed","has reviewed"]'::jsonb, 2,
   '未来の受動態は will be + 過去分詞。', 3),

  ('grammar',
   'She suggested ____ the meeting until next week.',
   '["to postpone","postponing","postpone","postponed"]'::jsonb, 1,
   'suggest は動名詞を目的語に取る。', 2),

  ('grammar',
   'Neither the manager nor the staff ____ aware of the change.',
   '["was","were","is","are"]'::jsonb, 0,
   'Neither A nor B では動詞は B（manager/staff のうち近い側）に合わせる。ここは staff が複数扱いだが、TOEIC では近接の名詞 staff を集合名詞として単数扱いにする例もあるが、本問では文法上 was を選ぶ。', 4),

  ('grammar',
   '____ the heavy rain, the outdoor event was held as planned.',
   '["Although","Despite","Because","While"]'::jsonb, 1,
   'Despite + 名詞句。Although は節を従える。', 3)
on conflict do nothing;

-- ---------- listening quiz ----------
insert into public.quiz_questions (skill_code, prompt, choices, answer_index, explanation, difficulty, passage) values
  ('listening',
   'What time will the meeting start?',
   '["At 9:00","At 9:30","At 10:00","At 10:30"]'::jsonb, 2,
   'The speaker says "Let''s move the meeting to ten in the morning."',
   2,
   'A: Are we still meeting at nine? B: Actually, let''s move the meeting to ten in the morning. A: Got it, ten it is.'),

  ('listening',
   'Where most likely is this conversation taking place?',
   '["At an airport","At a hotel front desk","At a restaurant","At a clothing store"]'::jsonb, 1,
   'Key clues: check-in, room, reservation.',
   2,
   'A: Hi, I have a reservation under Tanaka. B: Welcome. Your room is on the fourth floor, here is your key card.')
on conflict do nothing;

-- ---------- reading quiz ----------
insert into public.quiz_questions (skill_code, prompt, choices, answer_index, explanation, difficulty, passage) values
  ('reading',
   'According to the passage, why did the company change its policy?',
   '["To reduce costs","To improve employee well-being","To attract investors","To open a new branch"]'::jsonb, 1,
   'The passage states the company introduced the policy "to support our team''s well-being."',
   3,
   'Last quarter, Aoyama Foods introduced a four-day workweek to support our team''s well-being. While the change was initially met with concern from some managers, productivity remained stable and reported stress levels dropped noticeably.')
on conflict do nothing;

-- ---------- content_items: shadowing prompts ----------
insert into public.content_items (skill_code, title, body, difficulty, est_minutes) values
  ('shadowing',
   'Greeting a client at the office',
   jsonb_build_object(
     'script', 'Good morning. Thank you for coming all the way to our office. May I offer you a cup of coffee or tea before we start the meeting?',
     'tips',   '語尾を落とさず、語と語のつながり (linking) を意識して。'),
   2, 5),
  ('shadowing',
   'Confirming an order on the phone',
   jsonb_build_object(
     'script', 'I would like to confirm your order. That is two large boxes of paper and one printer cartridge, shipped to the main office. Is that correct?',
     'tips',   'I would like を I''d like と短く発音する練習を。'),
   3, 5)
on conflict do nothing;

-- ---------- content_items: reading passages ----------
insert into public.content_items (skill_code, title, body, difficulty, est_minutes) values
  ('reading',
   'A short notice from the building manager',
   jsonb_build_object(
     'passage', 'Please be advised that the elevator on the east side will be out of service from Monday to Wednesday next week for routine maintenance. The west elevator will remain available, but we expect longer wait times during business hours. Thank you for your patience.',
     'word_count', 50,
     'questions', jsonb_build_array(
       jsonb_build_object(
         'q', 'Why is the east elevator unavailable?',
         'a', 'routine maintenance'
       )
     )),
   2, 4),
  ('reading',
   'An email about a project deadline',
   jsonb_build_object(
     'passage', 'Hi team, due to a delay in receiving feedback from the client, we will be pushing the project deadline back by one week. Please update your schedules accordingly and let me know if this causes any conflicts with other work.',
     'word_count', 45,
     'questions', jsonb_build_array(
       jsonb_build_object(
         'q', 'What should team members do?',
         'a', 'Update their schedules and report conflicts.'
       )
     )),
   3, 4)
on conflict do nothing;

-- ---------- content_items: speaking prompts ----------
insert into public.content_items (skill_code, title, body, difficulty, est_minutes) values
  ('speaking',
   'Describe your typical workday',
   jsonb_build_object(
     'prompt', 'In 30 to 60 seconds, describe what a typical workday looks like for you. Include at least three activities.',
     'tips',   '時系列で First, Then, After that, Finally などの順序の語を使うと話しやすい。'),
   2, 3),
  ('speaking',
   'Explain a recent change at your workplace',
   jsonb_build_object(
     'prompt', 'Talk about a recent change at your workplace or in your studies. Was it positive or negative? Why?',
     'tips',   '結論 (positive/negative) を先に述べてから理由を 2つ述べる構成で。'),
   3, 3)
on conflict do nothing;

-- ---------- content_items: listening scripts ----------
insert into public.content_items (skill_code, title, body, difficulty, est_minutes) values
  ('listening',
   'Short office dialogue: rescheduling a meeting',
   jsonb_build_object(
     'script', 'A: Are we still meeting at nine? B: Actually, let''s move the meeting to ten in the morning. A: Got it, ten it is.',
     'glossary', jsonb_build_array(
       jsonb_build_object('term','move the meeting','meaning','会議をずらす'),
       jsonb_build_object('term','ten it is','meaning','じゃあ10時で')
     )),
   2, 3)
on conflict do nothing;
