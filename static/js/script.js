document.addEventListener('DOMContentLoaded', function() {
  const whatsappButton = document.querySelector('.whatsapp-button');
    
  const whatsappMessage = document.createElement('span');
  whatsappMessage.textContent = '¡Mándanos un mensaje!';
  whatsappMessage.style.position = 'absolute';
  whatsappMessage.style.bottom = '60px'; 
  whatsappMessage.style.left = '50%';
  whatsappMessage.style.transform = 'translateX(-50%)';
  whatsappMessage.style.backgroundColor = '#25d366';
  whatsappMessage.style.color = 'white';
  whatsappMessage.style.padding = '5px 10px';
  whatsappMessage.style.borderRadius = '10px';
  whatsappMessage.style.fontSize = '14px';
  whatsappMessage.style.display = 'none'; 
  whatsappButton.style.position = 'absolutee'; 
  whatsappButton.appendChild(whatsappMessage);

  whatsappButton.addEventListener('mouseenter', function() {
    whatsappMessage.style.display = 'inline-block'; 
  });

  whatsappButton.addEventListener('mouseleave', function() {
    whatsappMessage.style.display = 'none'; 
  });
});

document.addEventListener('DOMContentLoaded', function() {
  const darkModeToggle = document.getElementById('darkModeToggle');
  const htmlElement = document.documentElement;

  const darkModeEnabled = localStorage.getItem('darkMode') === 'true';
  if (darkModeEnabled) {
    htmlElement.setAttribute('data-bs-theme', 'dark');
  }

  darkModeToggle.addEventListener('click', function() {
    const isDarkMode = htmlElement.getAttribute('data-bs-theme') === 'dark';
    if (isDarkMode) {
      htmlElement.setAttribute('data-bs-theme', 'light');
      localStorage.setItem('darkMode', 'false');
    } else {
      htmlElement.setAttribute('data-bs-theme', 'dark');
      localStorage.setItem('darkMode', 'true');
    }
  });
});
