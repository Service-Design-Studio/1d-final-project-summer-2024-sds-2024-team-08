document.addEventListener('DOMContentLoaded', (event) => {
    setTimeout(() => {
      let alerts = document.querySelectorAll('.alert');
      alerts.forEach((alert) => {
        alert.classList.remove('show');
        alert.classList.add('hide');
      });
    }, 1500); 
    
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

      document.querySelectorAll('iframe').forEach(function(iframe) {
        iframe.addEventListener('load', function() {
            iframe.classList.add('iframe-loaded');
        });
      });
});