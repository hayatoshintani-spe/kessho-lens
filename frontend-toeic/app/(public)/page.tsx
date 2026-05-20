import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight, BookOpen, Headphones, Mic2, Sparkles } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      <header className="container flex items-center justify-between py-6">
        <div className="flex items-center gap-2 font-bold">
          <Sparkles className="h-5 w-5 text-blue-600" />
          <span>Kessho Lens English</span>
        </div>
        <Button asChild variant="ghost">
          <Link href="/login">ログイン</Link>
        </Button>
      </header>

      <main className="container py-16">
        <section className="mx-auto max-w-2xl text-center">
          <p className="mb-4 text-sm font-medium text-blue-600">
            TOEIC 500 → 900 の最短ルート
          </p>
          <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
            毎日の学習を、
            <br className="hidden sm:inline" />
            シンプルに可視化する。
          </h1>
          <p className="mt-6 text-base text-slate-600 sm:text-lg">
            単語・文法・リスニング・シャドーイング・英読・スピーキング。
            6つのスキルを、今日やるべき時間として表示します。
            学習時間・正答率・自己評価・録音をすべて1か所に。
          </p>
          <div className="mt-8 flex items-center justify-center gap-3">
            <Button size="lg" asChild>
              <Link href="/login">
                はじめる
                <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <Link href="#features">機能を見る</Link>
            </Button>
          </div>
        </section>

        <section id="features" className="mx-auto mt-24 grid max-w-4xl gap-6 sm:grid-cols-3">
          <FeatureCard
            icon={<BookOpen className="h-5 w-5 text-blue-600" />}
            title="今日のタスクを自動生成"
            body="あなたの目標と1日の学習時間から、6スキルの配分を自動で計算します。"
          />
          <FeatureCard
            icon={<Headphones className="h-5 w-5 text-teal-600" />}
            title="リスニング & 英読を計測"
            body="WPM・理解度・正答率を記録。週次でどこを伸ばすべきかが分かります。"
          />
          <FeatureCard
            icon={<Mic2 className="h-5 w-5 text-orange-600" />}
            title="録音 & 自己評価"
            body="シャドーイングとスピーキングは録音と5段階の自己評価で振り返れます。"
          />
        </section>
      </main>

      <footer className="container py-12 text-center text-xs text-slate-500">
        © Kessho Lens English — Built for serious learners.
      </footer>
    </div>
  );
}

function FeatureCard({
  icon,
  title,
  body,
}: {
  icon: React.ReactNode;
  title: string;
  body: string;
}) {
  return (
    <div className="rounded-xl border bg-white p-5 shadow-sm">
      <div className="mb-3">{icon}</div>
      <div className="font-semibold">{title}</div>
      <p className="mt-1 text-sm text-slate-600">{body}</p>
    </div>
  );
}
