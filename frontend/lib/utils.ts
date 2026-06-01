import { type ClassValue, clsx } from 'clsx';
import { format, parseISO, isValid } from 'date-fns';
import { ja } from 'date-fns/locale';

// ─── Tailwind class merging ───────────────────────────────────────────────────

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

// ─── Date formatting ──────────────────────────────────────────────────────────

export function formatDate(dateStr: string): string {
  try {
    const d = parseISO(dateStr);
    if (!isValid(d)) return dateStr;
    return format(d, 'yyyy年M月d日', { locale: ja });
  } catch {
    return dateStr;
  }
}

export function formatDatetime(dateStr: string): string {
  try {
    const d = parseISO(dateStr);
    if (!isValid(d)) return dateStr;
    return format(d, 'yyyy年M月d日 HH:mm', { locale: ja });
  } catch {
    return dateStr;
  }
}
