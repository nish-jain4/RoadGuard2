// language.js
import translations from "./translations.js";

let currentLang = localStorage.getItem("lang") || "en";

function setLanguage(lang) {
  currentLang = lang;
  localStorage.setItem("lang", lang);

  // update all text dynamically
  document.querySelectorAll("[data-translate]").forEach(el => {
    const key = el.getAttribute("data-translate");
    el.innerText = translations[lang][key] || key;
  });
}

// Initial load
document.addEventListener("DOMContentLoaded", () => {
  setLanguage(currentLang);

  // handle button click
  document.getElementById("langBtn").addEventListener("click", () => {
    const nextLang = currentLang === "en" ? "hi" : currentLang === "hi" ? "fr" : "en";
    setLanguage(nextLang);
  });
});
