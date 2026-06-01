import type { Metadata, Viewport } from 'next';
import './globals.css';
import Sidebar from '@/components/layout/Sidebar';
import Header from '@/components/layout/Header';

export const metadata: Metadata = {
  title: 'Tsuburaya Intelligence Brief',
  description:
    '外部ニュース・規制動向・技術トレンドを、円谷の事業機会・リスク・経営論点に翻訳して経営層に届けるインテリジェンス基盤',
  keywords: [
    'Tsuburaya Intelligence Brief',
    'インテリジェンス・ブリーフ',
    'IP戦略',
    'AI会議',
    '円谷',
  ],
};

export const viewport: Viewport = {
  themeColor: '#0B0E14',
  colorScheme: 'dark',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ja" className="dark">
      <body className="bg-bg-primary text-text-primary min-h-screen">
        <div className="flex min-h-screen">
          {/* Sidebar — hidden on mobile, shown on md+ */}
          <aside className="hidden md:flex flex-col fixed top-0 left-0 h-screen z-40">
            <Sidebar />
          </aside>

          {/* Main area */}
          <div className="flex-1 flex flex-col md:ml-[240px] min-h-screen">
            <Header />
            <main className="flex-1 p-4 md:p-6 lg:p-8 overflow-auto">
              {children}
            </main>
          </div>
        </div>
      </body>
    </html>
  );
}
