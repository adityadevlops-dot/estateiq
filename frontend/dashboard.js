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
    
    const response = await fetch('/api/metrics');
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

if (navbar) {
  window.addEventListener('scroll', () => {
    if (window.scrollY > 80) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  });
}

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
  
  // Validate target is a finite positive number
  if (isNaN(target) || target <= 0) {
    element.textContent = '0';
    element.dataset.animated = 'true';
    return;
  }
  
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
  row.addEventListener('mouseenter', () => {
    row.style.backgroundColor = 'rgba(200, 169, 110, 0.05)';
  });
  
  row.addEventListener('mouseleave', () => {
    row.style.backgroundColor = '';
  });
  
  row.addEventListener('click', () => {
    const firstTd = row.querySelector('td');
    if (firstTd) {
      console.log('✓ Row clicked:', firstTd.textContent);
    }
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

// ============================================================================
// API KEY MANAGEMENT
// ============================================================================

const copyApiKeyBtn = document.getElementById('copyApiKeyBtn');
if (copyApiKeyBtn) {
  copyApiKeyBtn.addEventListener('click', async (e) => {
    e.preventDefault();
    try {
      // In production, fetch API key from backend
      // const response = await fetch('/api/user/api-key');
      // const data = await response.json();
      // const apiKey = data.api_key;
      
      // For demo, use a mock API key
      const apiKey = 'sk_estateiq_' + Math.random().toString(36).substr(2, 20).toUpperCase();
      
      // Copy to clipboard
      await navigator.clipboard.writeText(apiKey);
      copyApiKeyBtn.textContent = '✓ Copied!';
      setTimeout(() => {
        copyApiKeyBtn.textContent = 'Copy';
      }, 2000);
      
      console.log('✓ API key copied to clipboard');
    } catch (error) {
      console.error('✗ Failed to copy API key:', error);
      alert('Failed to copy API key. Please try again.');
    }
  });
}

// ============================================================================
// DELETE ACCOUNT CONFIRMATION
// ============================================================================

const deleteAccountBtn = document.getElementById('deleteAccountBtn');
if (deleteAccountBtn) {
  deleteAccountBtn.addEventListener('click', (e) => {
    e.preventDefault();
    confirmDeleteAccount();
  });
}

function confirmDeleteAccount() {
  const confirmed = confirm(
    'Are you absolutely sure you want to delete your account?\n\n' +
    'This action CANNOT be undone. All your data, predictions, and API keys will be permanently deleted.\n\n' +
    'Type your password to confirm deletion.'
  );
  
  if (confirmed) {
    const password = prompt('Enter your password to confirm account deletion:');
    if (password) {
      deleteAccount(password);
    }
  }
}

async function deleteAccount(password) {
  try {
    // In production, call DELETE /api/auth/profile with password verification
    // const response = await Auth.delete('/api/auth/profile', { password });
    
    // For demo purposes
    console.log('✓ Account deletion confirmed');
    alert('Your account has been deleted. You will be logged out.');
    Auth.logout();
  } catch (error) {
    console.error('✗ Account deletion failed:', error);
    alert('Failed to delete account. Please try again.');
  }
}

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
