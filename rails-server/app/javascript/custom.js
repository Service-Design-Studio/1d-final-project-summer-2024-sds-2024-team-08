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
    const messagesDiv = document.getElementById("chat-history-child");

    form.addEventListener("submit", function (event) {
      if (inputField.value.trim() === "") {
        event.preventDefault(); // Prevent form submission if input is empty
      } else {
        // add user msg
        add_msg_to_div(messagesDiv, inputField.value, true);

        allElements.forEach((element) => element.classList.add("hidden"));
        loadingAnimation.classList.remove("d-none");

        event.preventDefault();

        // do POST here
        const formData = new FormData(form);

        fetch(form.action, {
          method: "POST",
          body: formData,
          headers: {
            "X-CSRF-Token": document
              .querySelector('meta[name="csrf-token"]')
              .getAttribute("content"),
          },
        })
          .then((response) => response.json())
          .then((data) => {
            res = data.reply;
            graph_id_res = data.graph_id;
            console.log("Success:", res);

            // dynamically add to DOM
            add_msg_to_div(messagesDiv, res);
          })
          .catch((error) => {
            console.error("Error:", error);
          })
          .finally(() => {
            // Hide loading animation
            loadingAnimation.classList.add("d-none");
            // show message input
            allElements.forEach((element) =>
              element.classList.remove("hidden")
            );

            // reset form input
            form.reset();
          });
      }
    });
  }

  const chatHistory = document.getElementById("center-content");
  if (chatHistory) {
    chatHistory.scrollTop = chatHistory.scrollHeight;
  }

  document.querySelectorAll("iframe").forEach(function (iframe) {
    iframe.addEventListener("load", function () {
      iframe.classList.add('loaded');
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

function add_msg_to_div(targetDiv, res, is_user = false) {
  let html_content;
  const chat_id = getChatIdFromPath();
  const chatHistory = document.getElementById("center-content");

  if (res.includes("The network graph has been created!")) {
    // Create an iframe to display the latest graph for the specific chat ID
    html_content = `
        <div class="row mb-3">
            <div class="d-flex justify-content-end w-100">
                <div id="message-content-${new Date().getTime()}" class="message-content ${is_user ? "user" : "genie"} rounded">
                    <iframe src="/g/latest/${chat_id}" scrolling="no" allowfullscreen class="loaded"></iframe>
                </div>
            </div>
        </div>
    `;
  } else {
    html_content = `
        <div class="row mb-3">
        <div class="d-flex ${is_user ? "justify-content-end" : "justify-content-start"} w-100">
          <div id="message-content-${new Date().getTime()}" class="message-content ${is_user ? "user" : "genie"} rounded d-flex align-items-start ${is_user ? "p-3" : ""}">
            ${
              !is_user
                ? `
                    <img alt="Genie Logo" class="genie-icon" src="/assets/genie_logo.svg"></img>
                    <p class="mb-0 ml-2">${res}</p>
                  `
                : `<p class="mb-0">${res}</p>`
            }
          </div>
        </div>
      </div>
    `;
  }
  if (!targetDiv) return;
  console.log("beforeinsert");
  targetDiv.insertAdjacentHTML("beforeend", html_content);
  chatHistory.scrollTop = chatHistory.scrollHeight;
}

function getChatIdFromPath() {
  const path = window.location.pathname;
  const parts = path.split("/");
  const chatIndex = parts.indexOf("c");
  if (chatIndex !== -1 && parts.length > chatIndex + 1) {
    return parts[chatIndex + 1];
  }
  return null;
}
