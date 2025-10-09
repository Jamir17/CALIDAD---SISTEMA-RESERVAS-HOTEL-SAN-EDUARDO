// static/js/index.js
document.addEventListener("DOMContentLoaded", () => {
  /* =========================
     1) Header: sombra al hacer scroll
     ========================= */
  const header = document.querySelector(".header");
  const onScroll = () => {
    if (!header) return;
    header.style.boxShadow =
      window.scrollY > 100 ? "0 4px 6px -1px rgba(0, 0, 0, 0.1)" : "none";
    // Si usas la clase 'scrolled' en CSS, descomenta:
    // document.body.classList.toggle("scrolled", window.scrollY > 4);
  };
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  /* =========================
     2) Scroll suave con compensación por header fijo
     ========================= */
  const headerH = () => (header ? header.offsetHeight : 0);

  function smoothScrollTo(selector) {
    const el = document.querySelector(selector);
    if (!el) return;
    const y =
      el.getBoundingClientRect().top + window.pageYOffset - headerH() - 8;
    window.scrollTo({ top: y, behavior: "smooth" });
  }

  // Enlaces internos (nav y cualquier ancla con hash)
  document.querySelectorAll('a[href^="#"]').forEach((link) => {
    link.addEventListener("click", (e) => {
      const hash = link.getAttribute("href");
      if (hash && hash.length > 1) {
        e.preventDefault();
        smoothScrollTo(hash);
      }
    });
  });

  // Si llega con hash en la URL (accesibilidad)
  if (window.location.hash) {
    setTimeout(() => smoothScrollTo(window.location.hash), 80);
  }

  /* =========================
     3) Tabs (Nuestros Servicios / Ubicación)
     ========================= */
  const tabButtons = document.querySelectorAll(".tab-button");
  const tabPanels = document.querySelectorAll(".tab-panel");

  function activateTab(targetId) {
    // Quitar estados
    tabButtons.forEach((b) => b.classList.remove("active"));
    tabPanels.forEach((p) => p.classList.remove("active"));
    // Activar destino
    const btn = Array.from(tabButtons).find(
      (b) => b.getAttribute("data-tab") === targetId
    );
    const panel = document.getElementById(targetId);
    if (btn) btn.classList.add("active");
    if (panel) panel.classList.add("active");
  }

  tabButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-tab");
      activateTab(targetId);

      // Llevar la vista a la sección de tabs para que el cambio se vea
      const tabsSection = document.querySelector(".tabs-section");
      if (tabsSection) {
        const y =
          tabsSection.getBoundingClientRect().top +
          window.pageYOffset -
          headerH() -
          8;
        window.scrollTo({ top: y, behavior: "smooth" });
      }
    });
  });

  // Estado inicial: respeta el botón marcado como .active o por defecto "servicios"
  const initialBtn = document.querySelector(".tab-button.active");
  activateTab(initialBtn ? initialBtn.getAttribute("data-tab") : "servicios");

  /* =========================
     4) Acciones de botones principales (UX)
     ========================= */
  // Hero
  document
    .querySelectorAll(".hero .btn-primary, .hero .btn-white")
    .forEach((btn) => {
      btn.addEventListener("click", () => {
        const text = (btn.textContent || "").toLowerCase();
        if (text.includes("reservar")) {
          smoothScrollTo("#reservas");
        } else if (text.includes("ver habitaciones")) {
          smoothScrollTo("#habitaciones");
        }
      });
    });

  // CTA
  const cta = document.querySelector(".cta-section");
  if (cta) {
    cta.querySelectorAll(".btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const t = (btn.textContent || "").toLowerCase();
        if (t.includes("contactar")) {
          smoothScrollTo("#nosotros");
        } else {
          smoothScrollTo("#reservas");
        }
      });
    });
  }

  /* =========================
     5) Intersection Observer: animaciones de aparición
     ========================= */
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.style.opacity = "1";
        entry.target.style.transform = "translateY(0)";
      });
    },
    { threshold: 0.1, rootMargin: "0px 0px -50px 0px" }
  );

  const animatedElements = document.querySelectorAll(
    ".service-card, .room-card, .gallery-item, .testimonial-card"
  );

  animatedElements.forEach((el) => {
    el.style.opacity = "0";
    el.style.transform = "translateY(20px)";
    el.style.transition = "opacity 0.6s ease, transform 0.6s ease";
    observer.observe(el);
    // Si quieres que ya estén visibles sin scroll, comenta las dos líneas de estilo arriba
  });
});
