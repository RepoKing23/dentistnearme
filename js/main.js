/* Dentist Pro — site scripts (no dependencies) */
(function () {
  "use strict";

  // Sticky header shadow
  var header = document.querySelector(".header");
  if (header) {
    var onScroll = function () {
      header.classList.toggle("is-scrolled", window.scrollY > 10);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  // Mobile nav
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    var setOpen = function (open) {
      nav.classList.toggle("is-open", open);
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    };
    toggle.addEventListener("click", function () {
      setOpen(!nav.classList.contains("is-open"));
    });
    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) setOpen(false);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") setOpen(false);
    });
  }

  // Before / after sliders
  document.querySelectorAll(".ba__frame").forEach(function (frame) {
    var range = frame.querySelector(".ba__range");
    if (!range) return;
    var update = function () {
      frame.style.setProperty("--pos", range.value + "%");
    };
    range.addEventListener("input", update);
    update();
  });

  // FAQ accordion
  document.querySelectorAll(".faq__q").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var open = btn.getAttribute("aria-expanded") === "true";
      btn.setAttribute("aria-expanded", String(!open));
      document.getElementById(btn.getAttribute("aria-controls")).hidden = open;
    });
  });

  // Prefill service from "Book" links: <a href="#book" data-service="Braces">
  document.addEventListener("click", function (e) {
    var link = e.target.closest("[data-service]");
    if (!link) return;
    var select = document.querySelector('.js-booking select[name="service"]');
    if (!select) return;
    var wanted = link.getAttribute("data-service");
    for (var i = 0; i < select.options.length; i++) {
      if (select.options[i].value === wanted) {
        select.selectedIndex = i;
        break;
      }
    }
  });

  // Booking form: validation + AJAX submit
  // Works with Formspree (set your form ID in the action) or Netlify Forms (fallback).
  var PH_MOBILE = /^(\+?63|0)9\d{9}$/;

  document.querySelectorAll(".js-booking").forEach(function (form) {
    var status = form.querySelector(".form__status");
    var dateInput = form.querySelector('input[type="date"]');
    if (dateInput) dateInput.min = new Date().toISOString().split("T")[0];

    var setError = function (field, msg) {
      var wrap = field.closest(".field");
      if (!wrap) return;
      var out = wrap.querySelector(".field__error");
      wrap.classList.toggle("has-error", !!msg);
      field.setAttribute("aria-invalid", msg ? "true" : "false");
      if (out) out.textContent = msg || "";
    };

    var validate = function () {
      var ok = true;
      form.querySelectorAll("input, select, textarea").forEach(function (f) {
        if (f.type === "hidden" || f.closest(".hp")) return;
        var msg = "";
        var val = (f.value || "").trim();
        if (f.required && f.type === "checkbox" && !f.checked) msg = "Please agree before submitting.";
        else if (f.required && !val) msg = "This field is required.";
        else if (f.name === "phone" && val && !PH_MOBILE.test(val.replace(/[\s-]/g, "")))
          msg = "Enter a valid PH mobile number, e.g. 0917 123 4567.";
        else if (f.type === "email" && val && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val))
          msg = "Enter a valid email address.";
        setError(f, msg);
        if (msg && ok) {
          ok = false;
          f.focus();
        }
      });
      return ok;
    };

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      status.className = "form__status";
      status.textContent = "";
      if (!validate()) return;

      var btn = form.querySelector('[type="submit"]');
      var label = btn.textContent;
      btn.disabled = true;
      btn.textContent = "Sending…";

      var data = new FormData(form);
      var action = form.getAttribute("action") || "";
      var useFormspree = action.indexOf("formspree.io") !== -1 && action.indexOf("YOUR_FORM_ID") === -1;

      var request = useFormspree
        ? fetch(action, { method: "POST", body: data, headers: { Accept: "application/json" } })
        : fetch("/", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: new URLSearchParams(data).toString()
          });

      request
        .then(function (res) {
          if (!res.ok) throw new Error("HTTP " + res.status);
          form.reset();
          status.className = "form__status is-success";
          status.textContent =
            "Thank you! Your request was sent. We'll call or text you shortly to confirm your appointment.";
          if (window.gtag) window.gtag("event", "generate_lead", { form: form.getAttribute("name") });
        })
        .catch(function () {
          status.className = "form__status is-error";
          status.innerHTML =
            'Sorry, we couldn\'t send your request. Please call or text us at <a href="tel:+639934953526">0993 495 3526</a>.';
        })
        .finally(function () {
          btn.disabled = false;
          btn.textContent = label;
        });
    });

    form.addEventListener("input", function (e) {
      if (e.target.closest(".field.has-error")) setError(e.target, "");
    });
  });

  // Footer year
  document.querySelectorAll(".js-year").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });
})();
