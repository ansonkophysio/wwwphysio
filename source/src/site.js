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
    }, { threshold: 0.08, rootMargin: "0px 0px -6% 0px" });
    items.forEach((el) => io.observe(el));
  } else {
    items.forEach((el) => el.classList.add("in"));
  }

  // A soft ripple where you tap buttons and cards
  if (!reduce) {
    document.addEventListener("pointerdown", (ev) => {
      const t = ev.target.closest(".pill, .card, .post-card, .featured, .steps li, .filters button, .tcard, .situations a, .next-read");
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

  // Short silent clips: play while on screen, never with reduced motion; the button pauses and resumes
  document.querySelectorAll("video.clip").forEach((v) => {
    const btn = v.parentElement.querySelector(".clip-btn");
    let held = reduce;
    const sync = () => {
      if (!btn) return;
      btn.classList.toggle("paused", v.paused);
      btn.setAttribute("aria-label", v.paused ? btn.dataset.play : btn.dataset.pause);
    };
    const start = () => { const p = v.play(); if (p) p.catch(() => {}); };
    v.addEventListener("play", sync);
    v.addEventListener("pause", sync);
    if (btn) btn.addEventListener("click", () => {
      if (v.paused) { held = false; start(); } else { held = true; v.pause(); }
    });
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(([e]) => {
        if (e.isIntersecting) { if (!held) start(); } else if (!v.paused) v.pause();
      }, { threshold: 0.25 }).observe(v);
    } else if (!held) start();
    sync();
  });

  // Close the phone menu when tapping elsewhere
  document.addEventListener("click", (ev) => {
    document.querySelectorAll("details.menu[open]").forEach((d) => {
      if (!d.contains(ev.target)) d.removeAttribute("open");
    });
  });

  // Articles: reading progress bar and the contents list that follows you
  const bar = document.querySelector(".progress");
  const body = document.querySelector(".article-body");
  if (bar && body) {
    const update = () => {
      const r = body.getBoundingClientRect();
      const total = r.height - window.innerHeight * 0.6;
      const done = Math.min(1, Math.max(0, -r.top / Math.max(total, 1)));
      bar.style.transform = `scaleX(${done})`;
    };
    update();
    window.addEventListener("scroll", update, { passive: true });
    window.addEventListener("resize", update);
  }
  const links = [...document.querySelectorAll(".toc a")];
  if (links.length && "IntersectionObserver" in window) {
    const byId = new Map(links.map((a) => [a.getAttribute("href").slice(1), a]));
    const seen = new Set();
    const mark = () => {
      const heads = [...byId.keys()].map((id) => document.getElementById(id)).filter(Boolean);
      let current = heads[0];
      for (const h of heads) if (h.getBoundingClientRect().top < window.innerHeight * 0.3) current = h;
      links.forEach((a) => a.classList.toggle("active", current && a.getAttribute("href") === "#" + current.id));
    };
    mark();
    window.addEventListener("scroll", mark, { passive: true });
  }
  document.querySelectorAll(".toc-mobile a").forEach((a) =>
    a.addEventListener("click", () => a.closest("details").removeAttribute("open")));

  // Articles index: filter by topic
  const group = document.querySelector(".filters");
  if (group) {
    group.addEventListener("click", (ev) => {
      const btn = ev.target.closest("button");
      if (!btn) return;
      const topic = btn.dataset.filter;
      group.querySelectorAll("button").forEach((b) => b.setAttribute("aria-pressed", String(b === btn)));
      document.querySelectorAll(".post-grid li").forEach((li) => {
        li.hidden = Boolean(topic) && li.dataset.topic !== topic;
      });
    });
  }
})();
