/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "../templates/**/*.html",
    "../apps/**/templates/**/*.html",
    "../themes/**/*.html",
    "./src/**/*.{js,ts}",
  ],
  theme: {
    extend: {
      colors: {
        // Palette is driven by CSS variables (see styles.css :root). A theme can
        // override those variables to recolor the entire public site at runtime.
        paper: "rgb(var(--color-paper) / <alpha-value>)",
        ink: "rgb(var(--color-ink) / <alpha-value>)",
        accent: "rgb(var(--color-accent) / <alpha-value>)",
      },
      fontFamily: {
        // Body text — Geist (clean, developer-native), self-hosted variable font.
        sans: [
          "Geist Variable",
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "Segoe UI",
          "sans-serif",
        ],
        // Display / headlines — Space Grotesk, a characterful grotesk.
        display: [
          "Space Grotesk Variable",
          "Geist Variable",
          "ui-sans-serif",
          "system-ui",
          "sans-serif",
        ],
        // Code, labels, metadata.
        mono: [
          "Geist Mono Variable",
          "ui-monospace",
          "SFMono-Regular",
          "Menlo",
          "monospace",
        ],
      },
    },
  },
  plugins: [],
};
