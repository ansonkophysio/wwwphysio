// wwwphysio.com: small interactions. The site works fully without this file.
(() => {
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Sections ease in as they scroll into view
  const items = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && !reduce) {
    const io = new IntersectionObserver((entries) => {
      for (const e of entries) {
        if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
      }
    }, { threshold: 0.12, rootMargin: "0px 0px -6% 0px" });
    items.forEach((el) => io.observe(el));
  } else {
    items.forEach((el) => el.classList.add("in"));
  }

  // A soft ripple where you tap buttons and cards
  if (!reduce) {
    document.addEventListener("pointerdown", (ev) => {
      const t = ev.target.closest(".pill, .card, .post-cards li, .steps li");
      if (!t) return;
      const r = t.getBoundingClientRect();
      const s = document.createElement("span");
      s.className = "ripple";
      s.style.left = ev.clientX - r.left + "px";
      s.style.top = ev.clientY - r.top + "px";
      s.style.setProperty("--rs", Math.ceil(Math.hypot(r.width, r.height) / 6));
      t.appendChild(s);
      s.addEventListener("animationend", () => s.remove());
    });
  }

  // Close the phone menu when tapping elsewhere
  document.addEventListener("click", (ev) => {
    document.querySelectorAll("details.menu[open]").forEach((d) => {
      if (!d.contains(ev.target)) d.removeAttribute("open");
    });
  });
})();
