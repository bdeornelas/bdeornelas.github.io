// Inizializza librerie quando il DOM è pronto
document.addEventListener('DOMContentLoaded', () => {
  // Lucide Icons
  try {
    if (window.lucide) lucide.createIcons();
  } catch (error) {
    console.error('Errore nell\'inizializzazione di Lucide:', error);
  }

  // AOS (Animate On Scroll)
  try {
    if (window.AOS) {
      AOS.init({
        duration: 700, // durata animazioni
        once: true,    // le animazioni avvengono una sola volta
        offset: 50     // offset dal viewport
      });
    }
  } catch (error) {
    console.error('Errore nell\'inizializzazione di AOS:', error);
  }

  // Menu mobile
  const mobileMenuButton = document.getElementById('mobile-menu-button');
  const mobileMenu = document.getElementById('mobile-menu');

  if (mobileMenuButton && mobileMenu) {
    mobileMenuButton.addEventListener('click', () => {
      mobileMenu.classList.toggle('hidden');
      mobileMenuButton.setAttribute(
        'aria-expanded',
        mobileMenu.classList.contains('hidden') ? 'false' : 'true'
      );
    });
  }

  // Chiudi menu mobile dopo il click su un link
  const allNavLinks = document.querySelectorAll('#mobile-menu a');
  allNavLinks.forEach(link => {
    link.addEventListener('click', () => {
      if (mobileMenu) mobileMenu.classList.add('hidden');
    });
  });
});
