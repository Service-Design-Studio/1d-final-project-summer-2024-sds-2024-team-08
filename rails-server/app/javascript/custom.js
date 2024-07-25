document.addEventListener("DOMContentLoaded", (event) => {
  setTimeout(() => {
    let alerts = document.querySelectorAll(".alert");
    alerts.forEach((alert) => {
      alert.classList.remove("show");
      alert.classList.add("hide");
    });
  }, 1500);

  const form = document.getElementById("message-form");
  if (form) {
    const loadingAnimation = document.getElementById("loading-animation");
    const inputField = document.getElementById("message-input");
    const formElements = form.querySelectorAll(".input-group");
    const allElements = [...formElements];

    form.addEventListener("submit", function (event) {
      if (inputField.value.trim() === "") {
        event.preventDefault(); // Prevent form submission if input is empty
      } else {
        allElements.forEach((element) => element.classList.add("hidden"));
        loadingAnimation.classList.remove("d-none");
      }
    });
  }

  const chatHistory = document.getElementById("center-content");
  if (chatHistory) {
    chatHistory.scrollTop = chatHistory.scrollHeight;
  }

  document.querySelectorAll("iframe").forEach(function (iframe) {
    iframe.addEventListener("load", function () {
      iframe.classList.add("iframe-loaded");
    });
  });

  document
    .getElementById("hamburger-menu")
    .addEventListener("click", function () {
      var sidebar = document.getElementById("sidebar");
      var mainContent = document.getElementById("main-content");
      var bottomSection = document.getElementById("bottom-section");

      sidebar.classList.toggle("collapsed-sidebar");

      if (sidebar.classList.contains("collapsed-sidebar")) {
        sidebar.style.position = "relative";
        mainContent.classList.replace("col-12", "col-9");
        mainContent.classList.replace("col-lg-12", "col-lg-10");
        bottomSection.style.maxWidth = "none";
      } else {
        sidebar.style.position = "fixed";
        mainContent.classList.replace("col-9", "col-12");
        mainContent.classList.replace("col-lg-10", "col-lg-12");
        bottomSection.style.maxWidth = "75vw";
      }
    });
});
