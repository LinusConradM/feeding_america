import * as echarts from "echarts/core";
import { LineChart, ScatterChart, CustomChart } from "echarts/charts";
import { GridComponent, TooltipComponent, MarkLineComponent } from "echarts/components";
import { SVGRenderer } from "echarts/renderers";

echarts.use([LineChart, ScatterChart, CustomChart, GridComponent, TooltipComponent, MarkLineComponent, SVGRenderer]);
export { echarts };

export const css = (n: string) => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
export const reduced = () => matchMedia("(prefers-reduced-motion: reduce)").matches;

const charts = new Map<string, echarts.ECharts>();
export function chart(id: string) {
  const el = document.getElementById(id)!;
  charts.get(id)?.dispose();
  const c = echarts.init(el, null, { renderer: "svg" });
  charts.set(id, c);
  return c;
}
addEventListener("resize", () => charts.forEach((c) => c.resize()));

export function base() {
  return {
    animation: !reduced(),
    textStyle: { fontFamily: "Inter, system-ui, sans-serif", color: css("--fg-2") },
    tooltip: { trigger: "axis", backgroundColor: css("--surface"), borderColor: css("--border"), textStyle: { color: css("--fg"), fontSize: 13 }, confine: true },
  } as any;
}
export const axis = () => ({
  axisLine: { lineStyle: { color: css("--border") } },
  axisTick: { show: false },
  axisLabel: { color: css("--muted"), fontSize: 12 },
  splitLine: { lineStyle: { color: css("--border-soft") } },
});

/** Re-render when the color scheme changes. */
export function onTheme(fn: () => void) {
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", fn);
  new MutationObserver(fn).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
}

export function readJSON<T = any>(id: string): T {
  return JSON.parse(document.getElementById(id)!.textContent!);
}
