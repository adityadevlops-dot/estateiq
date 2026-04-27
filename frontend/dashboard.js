// ============================================================================
// DASHBOARD PAGE INTERACTIONS
// ============================================================================

// ============================================================================
// NAVBAR SCROLL DETECTION
// ============================================================================

const navbar = document.querySelector('.navbar');

window.addEventListener('scroll', () => {
  if (window.scrollY > 80) {
    navbar.classList.add('scrolled');
  } else {
    navbar.classList.remove('scrolled');
  }
});

// ============================================================================
// SIDEBAR NAVIGATION
// ============================================================================

const sidebarItems = document.querySelectorAll('.sidebar-nav-item');

sidebarItems.forEach(item => {
  item.addEventListener('click', () => {
    sidebarItems.forEach(i => i.classList.remove('active'));
    item.classList.add('active');
  });
});

// ============================================================================
// INTERSECTION OBSERVER FOR ANIMATIONS
// ============================================================================

const observerOptions = {
  threshold: 0.1,
  rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      // Add animation class
      if (entry.target.classList.contains('in-view') || entry.target.classList.contains('in-view-delayed-1')) {
        entry.target.classList.add('in-view');
      }
      
      // Trigger counter animations
      const counters = entry.target.querySelectorAll('.counter');
      counters.forEach(counter => {
        animateCounter(counter);
      });
      
      observer.unobserve(entry.target);
    }
  });
}, observerOptions);

// Observe all cards with animation classes
document.querySelectorAll('.card[class*="in-view"]').forEach(el => {
  observer.observe(el);
});

// ============================================================================
// NUMBER COUNTER ANIMATION
// ============================================================================

function animateCounter(element) {
  // Check if already animated
  if (element.dataset.animated === 'true') return;
  
  const target = parseInt(element.getAttribute('data-target'), 10);
  const duration = 1200; // ms
  const increment = target / (duration / 16); // 60fps
  
  let current = 0;
  
  const counter = setInterval(() => {
    current += increment;
    
    if (current >= target) {
      current = target;
      clearInterval(counter);
      element.dataset.animated = 'true';
    }
    
    element.textContent = Math.floor(current).toLocaleString();
  }, 16);
}

// ============================================================================
// FILTER INTERACTIONS
// ============================================================================

const applyFiltersBtn = document.querySelector('.btn-primary');
const resetBtn = document.querySelector('.btn-text');

if (applyFiltersBtn && applyFiltersBtn.textContent.includes('Apply Filters')) {
  applyFiltersBtn.addEventListener('click', (e) => {
    e.preventDefault();
    console.log('✓ Filters applied');
    // Add any filter logic here
  });
}

if (resetBtn && resetBtn.textContent.includes('Reset')) {
  resetBtn.addEventListener('click', (e) => {
    e.preventDefault();
    // Reset all select elements
    document.querySelectorAll('select').forEach(select => {
      select.selectedIndex = 0;
    });
    document.querySelectorAll('input[type="number"]').forEach(input => {
      input.value = '';
    });
    console.log('✓ Filters reset');
  });
}

// ============================================================================
// TABLE INTERACTIONS
// ============================================================================

const tableRows = document.querySelectorAll('tbody tr');

tableRows.forEach(row => {
  row.addEventListener('hover', () => {
    row.style.backgroundColor = 'rgba(200, 169, 110, 0.05)';
  });
  
  row.addEventListener('click', () => {
    console.log('✓ Row clicked:', row.querySelector('td').textContent);
  });
});

// ============================================================================
// CHART ANIMATION - BAR CHART
// ============================================================================

// Animate bar widths on scroll
const chartObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      const bars = entry.target.querySelectorAll('[style*="width"]');
      bars.forEach((bar, index) => {
        const width = bar.style.width;
        bar.style.width = '0%';
        setTimeout(() => {
          bar.style.transition = 'width 1s var(--easing)';
          bar.style.width = width;
        }, index * 100);
      });
      chartObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.3 });

document.querySelectorAll('svg, [style*="chart"]').forEach(chart => {
  chartObserver.observe(chart);
});

// ============================================================================
// RESPONSIVE SIDEBAR TOGGLE (for mobile)
// ============================================================================

function handleResponsive() {
  const width = window.innerWidth;
  const sidebar = document.querySelector('.sidebar');
  
  if (width <= 768 && sidebar) {
    // Sidebar becomes horizontal on mobile
    // This is handled by CSS media queries
  }
}

window.addEventListener('resize', handleResponsive);
handleResponsive();

// ============================================================================
// INITIALIZE
// ============================================================================

console.log('✓ Dashboard initialized');

// Trigger animations for cards already in view on page load
setTimeout(() => {
  document.querySelectorAll('.card').forEach(card => {
    const rect = card.getBoundingClientRect();
    if (rect.top < window.innerHeight) {
      card.classList.add('in-view');
      const counters = card.querySelectorAll('.counter');
      counters.forEach(counter => {
        animateCounter(counter);
      });
    }
  });
}, 300);
