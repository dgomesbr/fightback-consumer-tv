import { defineConfig } from "astro/config";

// GitHub Pages serves a project repository from a subpath, so `base` has to be set or every
// asset and link resolves one level too high. Both values are read by the Pages workflow.
export default defineConfig({
  site: "https://dgomesbr.github.io",
  base: "/fightback-consumer-tv",
  trailingSlash: "ignore",
  output: "static",
  build: {
    format: "directory",
  },
  markdown: {
    shikiConfig: {
      theme: "github-dark-dimmed",
      wrap: true,
    },
  },
  devToolbar: {
    enabled: false,
  },
});
