/**
 * Format a YYYY-MM-DD date string (Django DateField) as a local date.
 *
 * `new Date("2026-03-06")` parses as UTC midnight → shows the previous day
 * in timezones west of UTC. Parsing with explicit year/month/day avoids this.
 */
export function fmtDate(s: string | null | undefined): string {
  if (!s) return '—';
  const [y, m, d] = s.split('-').map(Number);
  return new Date(y, m - 1, d).toLocaleDateString();
}
