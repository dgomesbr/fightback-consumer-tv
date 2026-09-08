import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

/**
 * The guides live at the repository root, not inside src/, so the same markdown file renders
 * on GitHub and on this site. A contributor reading guides/vendors/lg-webos.md in a pull
 * request sees what a reader will see, and there is no second copy to drift.
 */
export const collections = {
  guides: defineCollection({
    loader: glob({
      pattern: ["**/*.md", "!**/_*.md"],
      base: "../guides",
    }),
    schema: z
      .object({
        title: z.string().optional(),
        platform: z.string().optional(),
        brands: z.array(z.string()).optional(),
        generations: z.string().optional(),
        dns_field: z.string().optional(),
        dev_mode: z.union([z.string(), z.boolean()]).optional(),
        adb: z.union([z.string(), z.boolean()]).optional(),
        package_disable: z.union([z.string(), z.boolean()]).optional(),
        root: z.string().optional(),
        max_tier: z.union([z.number(), z.string()]).optional(),
        updated: z.union([z.string(), z.date()]).optional(),
      })
      .passthrough(),
  }),
};
