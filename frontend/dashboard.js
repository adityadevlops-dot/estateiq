// ============================================================================
// SIDEBAR NAVIGATION & SECTION SWITCHING
// ============================================================================

const sidebarItems = document.querySelectorAll('.sidebar-nav-item');
const sections = document.querySelectorAll('.section-content');

sidebarItems.forEach(item => {
  item.addEventListener('click', () => {
    // Remove active class from all items
    sidebarItems.forEach(i => i.classList.remove('active'));
    
    // Add active class to clicked item
    item.classList.add('active');
    
    // Get the section name
    const sectionName = item.getAttribute('data-section');
    
    // Hide all sections
    sections.forEach(section => {
      section.classList.remove('active');
    });
    
    // Show the selected section - be specific about finding .section-content
    const activeSection = document.querySelector(`.section-content[data-section="${sectionName}"]`);
    if (activeSection) {
      activeSection.classList.add('active');
      
      // Trigger animations on newly visible content
      const counters = activeSection.querySelectorAll('.counter');
      counters.forEach(counter => {
        if (counter.dataset.animated !== 'true') {
          animateCounter(counter);
        }
      });
    }
  });
});

// ============================================================================
// REPORTS GENERATION
// ============================================================================

const generateReportBtn = document.getElementById('generateReportBtn');
if (generateReportBtn) {
  generateReportBtn.addEventListener('click', () => {
    alert('📊 Report generation feature coming soon!\n\nYou will be able to:\n✓ Generate PDF reports\n✓ Export to CSV\n✓ Schedule automated reports\n✓ Download custom analytics');
    console.log('✓ Report generation initiated');
  });
}

// ============================================================================
// FETCH REAL METRICS FROM API
// ============================================================================

async function loadMetrics() {
  try {
    console.log('📊 Fetching metrics from backend API...');
    
    const response = await fetch('http://localhost:5000/api/metrics');
    if (!response.ok) throw new Error(`API error: ${response.status}`);
    
    const data = await response.json();
    console.log('✓ Metrics loaded:', data);
    
    if (data.success && data.data) {
      const metrics = data.data;
      
      // Update model accuracy
      const accuracyElement = document.querySelector('[data-metric="accuracy"]');
      if (accuracyElement) {
        accuracyElement.textContent = `${(metrics.model_r2_score * 100).toFixed(2)}%`;
      }
      
      // Update MAE
      const maeElement = document.querySelector('[data-metric="mae"]');
      if (maeElement) {
        const mae = Math.round(metrics.model_mae);
        maeElement.textContent = `₹${(mae / 100000).toFixed(2)}L`;
      }
      
      console.log('✓ Dashboard metrics updated with live data');
      return metrics;
    }
  } catch (error) {
    console.warn('⚠️ Could not load metrics from API:', error.message);
    console.warn('Using demo data instead');
  }
  
  return null;
}

// Load metrics on page load
document.addEventListener('DOMContentLoaded', () => {
  loadMetrics();
});

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
