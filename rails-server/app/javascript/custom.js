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
});