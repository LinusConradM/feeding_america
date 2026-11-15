import { geoPath, geoIdentity } from "d3-geo";
import { feature, mesh } from "topojson-client";
import { css, onTheme } from "./charts";

const BREAKS = [0.1, 0.125, 0.15, 0.175, 0.2];
const NS = "http://www.w3.org/2000/svg";

/** A static county choropleth: rates keyed by FIPS, same bins and colors as the Counties page. */
export function drawCountyMap(el: HTMLElement, rates: Record<string, number | null>, base: string) {
  fetch(base + "geo/us.json").then((r) => r.json()).then((topo) => {
    const states = feature(topo, topo.objects.states) as any;
    const path = geoPath(geoIdentity().reflectY(true).fitSize([975, 610], states));
    const svg = document.createElementNS(NS, "svg");
    svg.setAttribute("viewBox", "0 0 975 610");
    svg.setAttribute("aria-hidden", "true");
    const groups: Record<number, string[]> = {};
    for (const f of (feature(topo, topo.objects.counties) as any).features) {
      const v = rates[f.properties.id];
      const b = v == null ? -1 : BREAKS.filter((x) => v >= x).length;
      (groups[b] ??= []).push(path(f)!);
    }
    const layers: [number, SVGPathElement][] = Object.entries(groups).map(([b, ds]) => {
      const p = document.createElementNS(NS, "path");
      p.setAttribute("class", "c");
      p.setAttribute("d", ds.join(""));
      svg.append(p);
      return [Number(b), p];
    });
    const s = document.createElementNS(NS, "path");
    s.setAttribute("class", "s");
    s.setAttribute("d", path(mesh(topo, topo.objects.states, (a: any, b: any) => a !== b))!);
    svg.append(s);
    el.append(svg);
    const paint = () => {
      const cols = ["--q1", "--q2", "--q3", "--q4", "--q5", "--q6"].map(css);
      for (const [b, p] of layers) p.setAttribute("fill", b < 0 ? css("--nodata") : cols[b]);
    };
    paint();
    onTheme(paint);
  });
}
