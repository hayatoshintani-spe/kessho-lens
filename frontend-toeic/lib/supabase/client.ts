import { createBrowserClient } from "@supabase/ssr";

// Fallbacks keep `next build` from crashing in environments without env vars.
// Real values are inlined at build time when `.env.local` is configured.
const URL = process.env.NEXT_PUBLIC_SUPABASE_URL ?? "https://placeholder.supabase.co";
const KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? "placeholder-anon-key";

export const createSupabaseBrowserClient = () => createBrowserClient(URL, KEY);

