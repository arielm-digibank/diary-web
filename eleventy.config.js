import { EleventyHtmlBasePlugin } from "@11ty/eleventy";

export default function(eleventyConfig) {
  eleventyConfig.addPlugin(EleventyHtmlBasePlugin);

  // Pass through images without processing
  eleventyConfig.addPassthroughCopy("src/images");

  // Pass through entry pages as-is for now
  eleventyConfig.addPassthroughCopy("src/entries");

  return {
    dir: {
      input: "src",
      output: "_site",
      includes: "_includes",
      data: "_data"
    },
    htmlTemplateEngine: "njk",
    markdownTemplateEngine: "njk"
  };
};
