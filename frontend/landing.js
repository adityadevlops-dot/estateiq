// ============================================================================
// LANDING PAGE INTERACTIONS
// ============================================================================

// Navbar scroll detection
const navbar = document.querySelector('.navbar');
let lastScrollY = 0;

if (navbar) {
  window.addEventListener('scroll', () => {
    lastScrollY = window.scrollY;
    
    if (lastScrollY > 80) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }

    // Parallax effect on hero background
    const heroBg = document.querySelector('.hero-background');
    if (heroBg) {
      heroBg.style.transform = `translateY(${lastScrollY * 0.4}px)`;
    }
  });
}

// ============================================================================
// INTERSECTION OBSERVER FOR SCROLL ANIMATIONS
// ============================================================================

const observerOptions = {
  threshold: 0.1,
  rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add('in-view');
      
      // Trigger counter animations for this element
      const counters = entry.target.querySelectorAll('.counter');
      counters.forEach(counter => {
        animateCounter(counter);
      });
      
      observer.unobserve(entry.target);
    }
  });
}, observerOptions);

// Observe all elements with animation classes
document.querySelectorAll('[class*="in-view"]').forEach(el => {
  observer.observe(el);
});

// ============================================================================
// NUMBER COUNTER ANIMATION
// ============================================================================

function animateCounter(element) {
  const target = parseInt(element.getAttribute('data-target'), 10);
  const duration = 1200; // ms
  
  // Validate target is a finite positive number
  if (isNaN(target) || target <= 0) {
    element.textContent = '0';
    return;
  }
  
  const increment = target / (duration / 16); // 60fps
  
  let current = 0;
  
  const counter = setInterval(() => {
    current += increment;
    
    if (current >= target) {
      current = target;
      clearInterval(counter);
    }
    
    element.textContent = Math.floor(current).toLocaleString();
  }, 16);
}

// ============================================================================
// SMOOTH SCROLL FOR ANCHOR LINKS
// ============================================================================

document.querySelectorAll('a[href^="#"]').forEach(link => {
  link.addEventListener('click', (e) => {
    const href = link.getAttribute('href');
    if (href === '#') return;
    
    const target = document.querySelector(href);
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth' });
    }
  });
});

// ============================================================================
// CTA BUTTON ACTIONS
// ============================================================================

// Get Started button
document.querySelectorAll('.btn-outline').forEach(btn => {
  btn.addEventListener('click', () => {
    window.location.href = 'prediction.html';
  });
});

// Primary CTA buttons
document.querySelectorAll('.btn-primary').forEach(btn => {
  if (btn.textContent.includes('Predict Price') || btn.textContent.includes('Launch Dashboard')) {
    btn.addEventListener('click', () => {
      window.location.href = 'prediction.html';
    });
  }
});

// ============================================================================

// INITIAL SETUP
// ============================================================================

// Trigger initial scroll event to set navbar state
window.dispatchEvent(new Event('scroll'));

console.log('✓ Landing page initialized');
