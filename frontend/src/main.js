import "./styles.css";

// Self-hosted variable fonts (bundled by Vite, served from our own origin — no
// external CDN, no layout shift). Space Grotesk for display, Geist for body,
// Geist Mono for code/labels. Wired to Tailwind's font-display/sans/mono.
import "@fontsource-variable/space-grotesk";
import "@fontsource-variable/geist";
import "@fontsource-variable/geist-mono";

import Alpine from "alpinejs";

// Mark that JS is active so CSS can enable progressive-enhancement effects
// (e.g. .reveal scroll animations) without ever hiding content from no-JS users.
document.documentElement.classList.add("js");

// Self-contained scroll-reveal: any element with the `.reveal` class fades/rises
// in as it enters the viewport — no per-element directive to forget. No-JS users
// never reach here (content shows via CSS); reduced-motion users see no transition
// (the CSS start-state is gated on prefers-reduced-motion), so this only animates
// when it should. Each element is revealed once, then unobserved.
function initReveal() {
  const els = document.querySelectorAll(".reveal");
  if (!els.length) return;
  if (!("IntersectionObserver" in window)) {
    els.forEach((el) => el.classList.add("is-visible"));
    return;
  }
  const observer = new IntersectionObserver(
    (entries, obs) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          obs.unobserve(entry.target);
        }
      }
    },
    { rootMargin: "0px 0px -10% 0px", threshold: 0.1 },
  );
  els.forEach((el) => observer.observe(el));
}

initReveal();

window.Alpine = Alpine;
Alpine.start();
