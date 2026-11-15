export const pct = (v: number | null | undefined, d = 1) => (v == null ? "–" : (v * 100).toFixed(d) + "%");
export const pts = (v: number | null | undefined, d = 1) => (v == null ? "–" : v.toFixed(d) + "%");
export const num = (v: number | null | undefined) => (v == null ? "–" : v.toLocaleString("en-US"));
export const millions = (thousands: number) => (thousands / 1000).toFixed(1);
export const usd = (v: number | null | undefined) => (v == null ? "–" : "$" + v.toFixed(2));
export const bigUsd = (v: number | null | undefined) =>
  v == null ? "–" : v >= 1e6 ? "$" + (v / 1e6).toFixed(1) + " million" : "$" + v.toLocaleString("en-US");
const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
export const date = (iso: string | null | undefined) => {
  if (!iso) return "";
  const [y, m, d] = iso.slice(0, 10).split("-").map(Number);
  return `${MONTHS[m - 1]} ${d}, ${y}`;
};
export const esc = (s: unknown) =>
  String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]!);
