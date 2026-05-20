// Shared domain types. These are intentionally hand-written for the MVP
// rather than generated from Supabase, to keep the project bootable
// without a live database connection.

export type SkillCode =
  | "vocabulary"
  | "grammar"
  | "listening"
  | "shadowing"
  | "reading"
  | "speaking";

export const SKILL_CODES: SkillCode[] = [
  "vocabulary",
  "grammar",
  "listening",
  "shadowing",
  "reading",
  "speaking",
];

export const SKILL_LABEL: Record<SkillCode, string> = {
  vocabulary: "単語",
  grammar: "文法",
  listening: "リスニング",
  shadowing: "シャドーイング",
  reading: "英読",
  speaking: "スピーキング",
};

export const SKILL_RATIO: Record<SkillCode, number> = {
  vocabulary: 0.25,
  grammar: 0.15,
  listening: 0.25,
  shadowing: 0.15,
  reading: 0.15,
  speaking: 0.05,
};

export const SKILL_ROUTE: Record<SkillCode, string> = {
  vocabulary: "/study/vocabulary",
  grammar: "/study/grammar",
  listening: "/study/listening",
  shadowing: "/study/shadowing",
  reading: "/study/reading",
  speaking: "/study/speaking",
};

export type TaskStatus = "pending" | "in_progress" | "done" | "skipped";

export interface UserProfile {
  id: string;
  display_name: string | null;
  current_toeic: number | null;
  target_toeic: number | null;
  target_date: string | null;
  daily_minutes: number;
  weak_areas: SkillCode[];
  timezone: string;
  streak_count: number;
  last_studied_on: string | null;
  role: "user" | "admin";
  created_at: string;
  updated_at: string;
}

export interface DailyTask {
  id: string;
  user_id: string;
  task_date: string;
  skill_code: SkillCode;
  target_minutes: number;
  status: TaskStatus;
  content_item_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface LearningSession {
  id: string;
  user_id: string;
  skill_code: SkillCode;
  started_at: string;
  ended_at: string | null;
  duration_seconds: number;
  item_count: number;
  correct_count: number;
  accuracy: number | null;
  difficulty_avg: number | null;
  note: string | null;
  created_at: string;
  updated_at: string;
}

export interface VocabularyItem {
  id: string;
  word: string;
  meaning: string;
  part_of_speech: string | null;
  example_en: string | null;
  example_ja: string | null;
  difficulty: number;
  tags: string[] | null;
  created_at: string;
  updated_at: string;
}

export interface UserVocabularyReview {
  id: string;
  user_id: string;
  vocabulary_item_id: string;
  rating: "known" | "forgot" | "hard";
  interval_days: number;
  next_review_on: string;
  last_reviewed_at: string;
  repetition: number;
  ease: number;
  created_at: string;
  updated_at: string;
}

export interface QuizQuestion {
  id: string;
  skill_code: SkillCode;
  prompt: string;
  choices: string[];
  answer_index: number;
  explanation: string | null;
  difficulty: number;
  audio_path: string | null;
  passage: string | null;
  created_at: string;
  updated_at: string;
}

export interface QuizAttempt {
  id: string;
  user_id: string;
  quiz_question_id: string;
  session_id: string | null;
  selected_index: number;
  is_correct: boolean;
  elapsed_seconds: number;
  created_at: string;
}

export interface ContentItem {
  id: string;
  skill_code: SkillCode;
  title: string;
  body: Record<string, unknown>;
  difficulty: number;
  audio_path: string | null;
  est_minutes: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ShadowingAttempt {
  id: string;
  user_id: string;
  session_id: string | null;
  content_item_id: string | null;
  recording_path: string | null;
  self_rating: number;
  note: string | null;
  created_at: string;
}

export interface SpeakingAttempt {
  id: string;
  user_id: string;
  session_id: string | null;
  prompt: string;
  recording_path: string | null;
  self_rating: number;
  note: string | null;
  created_at: string;
}

export interface ReadingAttempt {
  id: string;
  user_id: string;
  session_id: string | null;
  content_item_id: string | null;
  read_seconds: number;
  word_count: number;
  wpm: number;
  comprehension: number;
  created_at: string;
}

export interface WeeklyReview {
  id: string;
  user_id: string;
  week_start: string;
  total_minutes: number;
  by_skill: Partial<Record<SkillCode, number>>;
  weakest_skill: SkillCode | null;
  top_skill: SkillCode | null;
  focus_next_week: SkillCode[] | null;
  note: string | null;
  created_at: string;
  updated_at: string;
}
