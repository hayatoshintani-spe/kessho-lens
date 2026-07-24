import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';

export default function BackLink({
  href,
  children,
}: {
  href: string;
  children: React.ReactNode;
}) {
  return (
    <Link
      href={href}
      className="inline-flex items-center gap-1 text-text-muted hover:text-accent-gold text-xs"
    >
      <ArrowLeft className="w-3 h-3" /> {children}
    </Link>
  );
}
