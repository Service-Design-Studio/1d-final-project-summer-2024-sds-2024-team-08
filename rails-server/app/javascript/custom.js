document.addEventListener('DOMContentLoaded', (event) => {
  setTimeout(() => {
    let alerts = document.querySelectorAll('.alert');
    alerts.forEach((alert) => {
      alert.classList.remove('show');
      alert.classList.add('hide');
    });
  }, 1500);

  document.getElementById('menu-toggle').addEventListener('click', function() {
    document.getElementById('sidebar').classList.toggle('hidden');
  });

  const form = document.getElementById('message-form');
  const actionButtons = document.getElementById('action-buttons');
  if (form) {
    const loadingAnimation = document.getElementById('loading-animation');
    const inputField = document.getElementById('message-input');
    const formElements = form.querySelectorAll('.input-group, .actions');
    const allElements = [...formElements, actionButtons];

    form.addEventListener('submit', function(event) {
      if (inputField.value.trim() === '') {
        event.preventDefault();  // Prevent form submission if input is empty
      } else {
        allElements.forEach(element => element.classList.add('hidden'));
        loadingAnimation.classList.remove('d-none');
      }
    });
  }

  const chatHistory = document.getElementById('chat-history');
  if (chatHistory) {
    chatHistory.scrollTop = chatHistory.scrollHeight;
  }

  var menuToggle = document.getElementById('menu-toggle');
  var sidebar = document.getElementById('sidebar');

  menuToggle.addEventListener('click', function() {
    if (sidebar.classList.contains('sidebar-hidden')) {
      sidebar.classList.remove('sidebar-hidden');
    } else {
      sidebar.classList.add('sidebar-hidden');
    }
  });

});