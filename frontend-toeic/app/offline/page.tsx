import Link from "next/link";
import { WifiOff } from "lucide-react";

export const metadata = {
  title: "オフライン — Kessho Lens English",
};

export default function OfflinePage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 p-6">
      <div className="max-w-md text-center">
        <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-slate-900 text-white">
          <WifiOff className="h-6 w-6" />
        </div>
        <h1 className="text-xl font-semibold">オフラインです</h1>
        <p className="mt-2 text-sm text-slate-600">
          インターネット接続が見つかりません。電波の届く場所で再度お試しください。
          一度開いた画面はキャッシュから表示されることがあります。
        </p>
        <Link
          href="/dashboard"
          className="mt-6 inline-flex items-center rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800"
        >
          ダッシュボードへ戻る
        </Link>
      </div>
    </div>
  );
}
