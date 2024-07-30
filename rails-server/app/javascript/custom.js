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
    const messagesDiv = document.getElementById("chat-history-child")

    form.addEventListener("submit", function (event) {
        if (inputField.value.trim() === "") {
            event.preventDefault(); // Prevent form submission if input is empty
        } else {
            // add user msg 
            add_msg_to_div(messagesDiv, inputField.value, true)

            allElements.forEach((element) => element.classList.add("hidden"));
            loadingAnimation.classList.remove("d-none");

            event.preventDefault()

            // do POST here 
            const formData = new FormData(form);

            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
                }
            })
            .then(response => response.json())
            .then(data => {
                res = data.reply
                console.log('Success:', res);

                // dynamically add to DOM 
                add_msg_to_div(messagesDiv, res)
            }).catch(error => {
                console.error('Error:', error);
            }).finally(() => {
                // Hide loading animation
                loadingAnimation.classList.add('d-none');
                // show message input 
                allElements.forEach((element) => element.classList.remove("hidden"));

                // reset form input 
                form.reset()
            })
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

function add_msg_to_div(targetDiv, res, is_user = false) {
    let html_content = `
        <div class="row mb-3">
            <div class="col-12 d-flex justify-content-end">
                <div id="message-content-1291" class="message-content ${is_user? 'user' : 'genie'} p-3 rounded">
                <div class="d-flex align-items-start">
                    ${
                        !is_user? 
                            `
                            <img alt="Genie Logo" class="genie-icon" src="/assets/genie_logo-b131754a9a7c6feda0e0ff88c222e64bb4f2f68ff97e1c884a5c6513e1c8561a.svg"></img>
                            <p class="mb-0 ml-2">${res}</p>
                            ` 
                        : 
                            `<p class="mb-0">${res}</p>`
                    }
                </div>
                </div>
            </div>
        </div>
    `

    if (!targetDiv) return 
    console.log("beforeinsert");
    targetDiv.insertAdjacentHTML("beforeend", html_content)
}