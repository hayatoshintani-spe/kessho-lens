import { redirect } from "next/navigation";
import { Sidebar } from "@/components/layout/Sidebar";
import { MobileNav } from "@/components/layout/MobileNav";
import { AppHeader } from "@/components/layout/AppHeader";
import { createSupabaseServerClient } from "@/lib/supabase/server";

export default async function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const supabase = createSupabaseServerClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) redirect("/login");

  const { data: profile } = await supabase
    .from("user_profiles")
    .select("display_name, onboarded_at")
    .eq("id", user.id)
    .maybeSingle();

  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar />
      <div className="flex min-h-screen flex-1 flex-col">
        <AppHeader email={user.email} displayName={profile?.display_name ?? null} />
        <main className="flex-1 p-4 pb-20 md:p-8 md:pb-8">{children}</main>
        <MobileNav />
      </div>
    </div>
  );
}
