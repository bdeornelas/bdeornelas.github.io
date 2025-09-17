// Inizializza librerie quando il DOM è pronto
document.addEventListener('DOMContentLoaded', () => {
  // Lucide Icons
  if (window.lucide) lucide.createIcons();

  // AOS
  if (window.AOS) AOS.init({
    duration: 700,
    once: true,
    offset: 50
  });

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

  // Navigazione “Ricerca” come pagina separata
  const mainWrapper = document.getElementById('main-content-wrapper');
  const researchWrapper = document.getElementById('research-content-wrapper');
  const allNavLinks = document.querySelectorAll('header a[href]');

  allNavLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      const target = link.getAttribute('href');

      if (target === '#ricerca') {
        e.preventDefault();
        if (mainWrapper && researchWrapper) {
          mainWrapper.classList.add('hidden');
          researchWrapper.classList.remove('hidden');
          window.scrollTo({ top: 0, behavior: 'smooth' });
        }
      } else {
        if (mainWrapper && researchWrapper && mainWrapper.classList.contains('hidden')) {
          mainWrapper.classList.remove('hidden');
          researchWrapper.classList.add('hidden');

          if (target && target.startsWith('#') && document.querySelector(target)) {
            e.preventDefault();
            setTimeout(() => {
              document.querySelector(target).scrollIntoView({ behavior: 'smooth' });
            }, 50);
          }
        }
      }

      if (mobileMenu) mobileMenu.classList.add('hidden');
    });
  });
});

