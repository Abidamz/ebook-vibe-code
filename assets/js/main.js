/* ═══════════════════════════════════════════════════════════════
   Digital Product Cash Machine — site scripts
   ═══════════════════════════════════════════════════════════════ */

/* ── CONFIG — EDIT THESE TWO LINES BEFORE GOING LIVE ──────────── */
const BUY_URL = "https://selar.co/your-playbook-product-link";      // ← PASTE your real Selar product link here
const WHATSAPP_NUMBER = "234XXXXXXXXXX";                            // ← your WhatsApp number (country code, no +)
/* ─────────────────────────────────────────────────────────────── */

document.addEventListener("DOMContentLoaded", () => {

  /* Wire up all buy buttons */
  const waMsg = encodeURIComponent(
    "Hello! I want to order the Digital Product Cash Machine ebook (₦3,500). Please send payment details."
  );
  const waHref = `https://wa.me/${WHATSAPP_NUMBER}?text=${waMsg}`;

  document.querySelectorAll("[data-buy]").forEach((btn) => {
    btn.setAttribute("href", BUY_URL);
    btn.setAttribute("target", "_blank");
    btn.setAttribute("rel", "noopener");
  });

  const wa1 = document.getElementById("whatsappLink");
  const wa2 = document.getElementById("whatsappLink2");
  if (wa1) wa1.setAttribute("href", waHref);
  if (wa2) wa2.setAttribute("href", waHref);

  /* Sticky nav shadow */
  const nav = document.getElementById("nav");
  const onScroll = () => nav.classList.toggle("scrolled", window.scrollY > 10);
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  /* Sticky Buy Now bar — appears after the hero */
  const buyBar = document.getElementById("buyBar");
  if (buyBar) {
    const onScroll2 = () => {
      const show = window.scrollY > 600;
      buyBar.classList.toggle("show", show);
      buyBar.setAttribute("aria-hidden", show ? "false" : "true");
    };
    onScroll2();
    window.addEventListener("scroll", onScroll2, { passive: true });
  }

  /* Mobile nav */
  const burger = document.getElementById("navBurger");
  const links = document.getElementById("navLinks");
  burger.addEventListener("click", () => {
    burger.classList.toggle("open");
    links.classList.toggle("open");
  });
  links.querySelectorAll("a").forEach((a) =>
    a.addEventListener("click", () => {
      burger.classList.remove("open");
      links.classList.remove("open");
    })
  );

  /* FAQ accordion */
  const faqItems = document.querySelectorAll(".faq-item");
  faqItems.forEach((item) => {
    const q = item.querySelector(".faq-q");
    const a = item.querySelector(".faq-a");
    q.addEventListener("click", () => {
      const isOpen = item.classList.contains("open");
      /* close others */
      faqItems.forEach((other) => {
        other.classList.remove("open");
        other.querySelector(".faq-a").style.maxHeight = "0px";
      });
      if (!isOpen) {
        item.classList.add("open");
        a.style.maxHeight = a.scrollHeight + "px";
      }
    });
  });

  /* Reveal on scroll */
  const revealEls = document.querySelectorAll(
    ".grid-4 > *, .steps-grid > *, .toc-grid > *, .step-row, .country-row > *, .bonus-wrap, .price-card, .author-wrap, .faq-list"
  );
  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.add("reveal", "visible");
            io.unobserve(e.target);
          }
        });
      },
      { threshold: 0.12 }
    );
    revealEls.forEach((el) => {
      el.classList.add("reveal");
      io.observe(el);
    });
  }
});
