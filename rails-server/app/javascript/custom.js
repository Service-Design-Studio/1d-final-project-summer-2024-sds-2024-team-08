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
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 160" class ="genie-icon">
                        <g clip-path="url(#clip0_5716_30627)">
                            <path d="M80 152C119.488 152 151.5 119.988 151.5 80.5C151.5 41.0116 119.488 9 80 9C40.5116 9 8.5 41.0116 8.5 80.5C8.5 119.988 40.5116 152 80 152Z" fill="#E5F8FF"></path>
                            <mask id="mask0_5716_30627" style="mask-type: alpha;" maskUnits="userSpaceOnUse" x="8" y="9" width="144" height="143">
                            <path d="M80 152C119.488 152 151.5 119.988 151.5 80.5C151.5 41.0116 119.488 9 80 9C40.5116 9 8.5 41.0116 8.5 80.5C8.5 119.988 40.5116 152 80 152Z" fill="#00B5FE"></path>
                            </mask>
                            <g mask="url(#mask0_5716_30627)">
                            <path d="M143.771 46.3605L106.41 46.2027C106.41 40.0326 109.925 38.8178 113.661 37.8158C117.397 36.8138 119.078 30.0319 125.57 29.646C129.404 29.418 131.415 30.3937 133.08 31.6501C133.083 31.6523 133.083 31.6545 133.085 31.6545C137.257 36.0935 140.847 41.0344 143.771 46.3605Z" fill="white"></path>
                            <path d="M38.1306 92.6069L9.39183 92.7388C8.90094 89.5479 8.60306 86.3268 8.5 83.0954C14.795 82.147 14.1512 76.8268 21.6687 77.3103C27.2459 77.6665 28.6946 83.9327 31.903 84.858C35.1114 85.7832 38.1306 86.9085 38.1306 92.6069Z" fill="white"></path>
                            </g>
                            <path d="M94.1536 69.5746C96.4361 63.3985 120.915 79.1731 125.937 85.691C130.959 92.209 99.5697 104.54 96.621 127.675C94.9688 140.639 89.2132 149.39 79.1751 157.165C83.2738 140.595 83.661 127.346 64.6469 117.871C45.6328 108.395 28.6525 92.102 34.8019 85.691C40.9513 79.2801 63.4799 64.2217 65.8816 69.5746C70.2223 79.249 77.2634 88.0897 80.3481 88.0897C83.4329 88.0897 89.8593 81.1945 94.1536 69.5746Z" fill="#00B5FE"></path>
                            <path d="M78.3907 12.1745C78.8395 10.5076 81.2046 10.5076 81.6534 12.1745L83.9115 20.5611C86.4162 29.8637 93.6826 37.1301 102.985 39.6348L111.372 41.8929C113.039 42.3417 113.039 44.7068 111.372 45.1556L102.985 47.4137C93.6826 49.9184 86.4162 57.1848 83.9115 66.4874L81.6534 74.874C81.2046 76.5409 78.8395 76.5409 78.3907 74.874L76.1326 66.4874C73.6279 57.1848 66.3615 49.9184 57.0589 47.4137L48.6723 45.1556C47.0054 44.7068 47.0054 42.3417 48.6723 41.8929L57.0589 39.6348C66.3615 37.1301 73.6279 29.8637 76.1326 20.5611L78.3907 12.1745Z" fill="#00B5FE"></path>
                            <path d="M47.5371 4.38267C47.7338 3.65239 48.7699 3.65239 48.9665 4.38267L49.9558 8.05678C51.0531 12.1322 54.2365 15.3156 58.3119 16.4129L61.986 17.4021C62.7163 17.5988 62.7163 18.6349 61.986 18.8315L58.3119 19.8207C54.2364 20.918 51.0531 24.1014 49.9558 28.1768L48.9665 31.851C48.7699 32.5812 47.7338 32.5812 47.5371 31.851L46.5479 28.1768C45.4506 24.1014 42.2672 20.918 38.1918 19.8207L34.5177 18.8315C33.7874 18.6349 33.7874 17.5988 34.5177 17.4021L38.1918 16.4129C42.2672 15.3156 45.4506 12.1322 46.5479 8.05678L47.5371 4.38267Z" fill="#00B5FE"></path>
                        </g>
                    </svg>
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
