/* uase_nigeria/static/uase_nigeria/js/script.js */

/* ========= NAVIGATION TOGGLE (Mobile Menu) ========= */
const navToggle = document.querySelector(".nav-toggle");
const navMenu = document.querySelector(".nav-menu");

if (navToggle) {
  navToggle.addEventListener("click", () => {
    navMenu.classList.toggle("active");
    navToggle.classList.toggle("open");
  });
}

/* ========= SMOOTH SCROLLING ========= */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener("click", function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute("href"));
    if (target) {
      target.scrollIntoView({ behavior: "smooth" });
    }
  });
});

/* ========= STICKY NAVBAR ========= */
window.addEventListener("scroll", () => {
  const header = document.querySelector("header");
  if (header) {
    header.classList.toggle("sticky", window.scrollY > 50);
  }
});

/* ========= SCROLL ANIMATIONS ========= */
const revealElements = document.querySelectorAll(".reveal");

function revealOnScroll() {
  const windowHeight = window.innerHeight;
  const revealPoint = 100;

  revealElements.forEach(el => {
    const revealTop = el.getBoundingClientRect().top;
    if (revealTop < windowHeight - revealPoint) {
      el.classList.add("active");
    } else {
      el.classList.remove("active");
    }
  });
}

window.addEventListener("scroll", revealOnScroll);

/* ========= BACK TO TOP BUTTON ========= */
const backToTop = document.querySelector(".back-to-top");

if (backToTop) {
  window.addEventListener("scroll", () => {
    if (window.scrollY > 400) {
      backToTop.classList.add("show");
    } else {
      backToTop.classList.remove("show");
    }
  });

  backToTop.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
}

/* ========= SIMPLE FORM VALIDATION ========= */
const contactForm = document.querySelector("#contact-form");

if (contactForm) {
  contactForm.addEventListener("submit", (e) => {
    const name = contactForm.querySelector("input[name='name']");
    const email = contactForm.querySelector("input[name='email']");
    const message = contactForm.querySelector("textarea[name='message']");
    let valid = true;

    if (!name.value.trim()) {
      alert("Please enter your name.");
      valid = false;
    } else if (!email.value.trim() || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
      alert("Please enter a valid email.");
      valid = false;
    } else if (!message.value.trim()) {
      alert("Please enter a message.");
      valid = false;
    }

    if (!valid) {
      e.preventDefault();
    }
  });
}
