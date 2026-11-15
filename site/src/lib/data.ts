import meta from "../data/meta.json";
import national from "../data/national.json";
import usdaStates from "../data/usda_states.json";
import mmgStates from "../data/mmg_states.json";
import counties from "../data/counties.json";
import snap from "../data/snap.json";
import { date } from "./format";

export { meta, national, usdaStates, mmgStates, counties, snap };

export type Src = { short: string; title: string; when: string; note: string; url: string };

const editionsByNumber = Object.fromEntries((meta as any).mmg_editions.map((e: any) => [e.edition, e]));

export function mmgFileDate(edition: number) {
  const e = editionsByNumber[edition];
  return e?.release_date ? `File dated ${date(e.release_date)}` : "Release date not published";
}

/** Source line for one Map the Meal Gap data year. */
export function mmgYearSource(year: number): Src {
  const orig = year + 2;
  const file = (meta as any).mmg_editions.find((e: any) => e.data_years.includes(year));
  const republished = file && file.edition !== orig;
  const when = file?.release_date
    ? republished
      ? `First published in MMG ${orig}; values from the MMG ${file.edition}${file.version ? " " + file.version : ""} file dated ${date(file.release_date)}`
      : `Released ${date(file.release_date)}`
    : `MMG ${orig}. Release date not published`;
  return {
    short: `Map the Meal Gap ${orig} (${year} data)` + (file?.release_date && !republished ? ` · ${date(file.release_date)}` : ""),
    title: `Feeding America, Map the Meal Gap ${orig}, ${year} data`,
    when,
    note: "Modeled estimate. The county and state files do not include confidence intervals.",
    url: (meta as any).sources.mmg.url,
  };
}

export const usdaSrc = (detail: string): Src => {
  const u = (meta as any).sources.usda;
  return { short: `${u.short} · ${date(u.release_date)}`, title: u.title, when: `Report dated ${date(u.release_date)}`, note: detail, url: u.url };
};

export const derivedSrc = (inputs: string): Src => ({
  short: "Calculated on this site",
  title: "Derived figure, not published by any source",
  when: `Inputs: ${inputs}`,
  note: "Computed by this project's pipeline from the stored source files. See Methods for the calculation.",
  url: import.meta.env.BASE_URL + "methods/#derived",
});
