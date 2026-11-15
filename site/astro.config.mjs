import { defineConfig } from "astro/config";

export default defineConfig({
  site: "https://linusconradm.github.io",
  base: "/feeding_america",
  trailingSlash: "always",
  build: { format: "directory" },
});
