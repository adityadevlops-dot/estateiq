// ============================================================================
// PREDICTION PAGE INTERACTIONS
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
// SEGMENTED BUTTON GROUPS
// ============================================================================

function initSegmentedGroups() {
  const groups = document.querySelectorAll('.segmented-group');
  
  groups.forEach(group => {
    const buttons = group.querySelectorAll('.segmented-btn');
    const groupId = group.id;
    
    buttons.forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        
        // Remove active class from all buttons in this group
        buttons.forEach(b => b.classList.remove('active'));
        
        // Add active class to clicked button
        btn.classList.add('active');
        
        // Store selected value
        const value = btn.getAttribute('data-value');
        sessionStorage.setItem(`selected-${groupId}`, value);
        
        console.log(`✓ Selected ${groupId}: ${value}`);
      });
    });
  });
}

initSegmentedGroups();

// ============================================================================
// RANGE SLIDER VALUE DISPLAY
// ============================================================================

const ageSlider = document.getElementById('age');
const ageOutput = document.getElementById('ageOutput');

if (ageSlider && ageOutput) {
  ageSlider.addEventListener('input', (e) => {
    ageOutput.textContent = e.target.value;
  });
  
  // Initialize
  ageOutput.textContent = ageSlider.value;
}

// ============================================================================
// TOGGLE SWITCH
// ============================================================================

const parkingToggle = document.getElementById('parking');
const parkingLabel = document.getElementById('parkingLabel');

if (parkingToggle && parkingLabel) {
  parkingToggle.addEventListener('change', (e) => {
    parkingLabel.textContent = e.target.checked ? 'Yes' : 'No';
  });
}

// ============================================================================
// AMENITY PILL TAGS
// ============================================================================

const pillTags = document.querySelectorAll('.pill-tag');
const selectedAmenities = new Set();

pillTags.forEach(tag => {
  tag.addEventListener('click', (e) => {
    e.preventDefault();
    
    const amenity = tag.getAttribute('data-amenity');
    
    if (tag.classList.contains('active')) {
      tag.classList.remove('active');
      selectedAmenities.delete(amenity);
    } else {
      tag.classList.add('active');
      selectedAmenities.add(amenity);
    }
    
    console.log('✓ Selected amenities:', Array.from(selectedAmenities));
  });
});

// ============================================================================
// FORM VALIDATION & SUBMISSION
// ============================================================================

const form = document.getElementById('predictionForm');
const submitBtn = form.querySelector('button[type="submit"]');
const loadingSpinner = document.getElementById('loadingSpinner');
const outputPlaceholder = document.getElementById('outputPlaceholder');
const resultCard = document.getElementById('resultCard');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  // Validate form
  if (!validateForm()) {
    console.error('✗ Form validation failed');
    return;
  }
  
  // Get form data
  const formData = getFormData();
  console.log('✓ Form data:', formData);
  
  // Show loading state
  showLoadingState();
  
  // Simulate API call
  try {
    const result = await simulatePrediction(formData);
    
    // Hide loading
    hideLoadingState();
    
    // Display result
    displayResult(result);
  } catch (error) {
    console.error('✗ Prediction error:', error);
    hideLoadingState();
  }
});

// ============================================================================
// FORM VALIDATION
// ============================================================================

function validateForm() {
  const area = document.getElementById('area').value;
  const location = document.getElementById('location').value;
  const bedroom = sessionStorage.getItem('selected-bedroomGroup');
  const bathroom = sessionStorage.getItem('selected-bathroomGroup');
  
  if (!area || area < 100 || area > 50000) {
    alert('Please enter a valid area between 100-50000 sq ft');
    return false;
  }
  
  if (!location) {
    alert('Please select a location');
    return false;
  }
  
  if (!bedroom) {
    alert('Please select number of bedrooms');
    return false;
  }
  
  if (!bathroom) {
    alert('Please select number of bathrooms');
    return false;
  }
  
  return true;
}

// ============================================================================
// GET FORM DATA
// ============================================================================

function getFormData() {
  return {
    area_sqft: parseInt(document.getElementById('area').value),
    location: document.getElementById('location').value,
    bedrooms: parseInt(sessionStorage.getItem('selected-bedroomGroup')),
    bathrooms: parseInt(sessionStorage.getItem('selected-bathroomGroup')),
    age_years: parseInt(document.getElementById('age').value),
    floor: parseInt(document.getElementById('floor').value) || 1,
    furnishing: sessionStorage.getItem('selected-furnishingGroup') || 'Unfurnished',
    parking: document.getElementById('parking').checked ? 1 : 0
  };
}

// ============================================================================
// PREDICTION API (Real Backend)
// ============================================================================

async function simulatePrediction(formData) {
  try {
    console.log('🔄 Calling backend API with data:', formData);
    
    // Call real backend API using authenticated request
    const response = await Auth.post('http://localhost:5000/api/predict', formData);
    
    if (!response || !response.ok) {
      const errorData = response ? await response.json().catch(() => ({})) : {};
      throw new Error(`Backend error: ${response?.status} - ${errorData.error || errorData.errors?.[0] || 'Unknown error'}`);
    }
    
    const data = await response.json();
    console.log('✓ Backend response:', data);
    
    if (!data.success || !data.data) {
      throw new Error(data.error || 'Invalid response format');
    }
    
    // Transform backend response to UI format
    const predictedPrice = parseInt(data.data.predicted_price);
    const confidence = Math.round((data.data.confidence_range?.confidence || 85) * 100) / 100;
    const minPrice = Math.round(data.data.confidence_range?.min_price || predictedPrice * 0.9);
    const maxPrice = Math.round(data.data.confidence_range?.max_price || predictedPrice * 1.1);
    
    // Extract feature importances and convert to percentages
    const features = {};
    const importances = data.data.feature_importances || {};
    
    // Top 5 features
    const topFeatures = Object.entries(importances)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 5);
    
    let totalImportance = topFeatures.reduce((sum, [, val]) => sum + val, 0);
    
    topFeatures.forEach(([feature, importance]) => {
      features[feature] = Math.round((importance / totalImportance) * 100);
    });
    
    // Ensure we have at least 100%
    if (Object.values(features).reduce((a, b) => a + b, 0) < 100) {
      features['other'] = 100 - Object.values(features).reduce((a, b) => a + b, 0);
    }
    
    return {
      predictedPrice,
      minPrice,
      maxPrice,
      confidence: Math.round(confidence),
      features
    };
    
  } catch (error) {
    console.error('✗ API call failed:', error.message);
    
    // Fallback: Show user-friendly error and use mock data for demo
    const errorMsg = error.message.includes('Failed to fetch') 
      ? 'Cannot connect to backend API. Ensure server is running on http://localhost:5000'
      : error.message;
    
    alert(`⚠️ Backend Connection Error\n\n${errorMsg}\n\nUsing demo data for this prediction.`);
    
    // Fallback mock prediction
    const locationMultipliers = {
      'Mumbai': 2.5, 'Bangalore': 1.8, 'Delhi': 1.9, 'Pune': 1.4,
      'Hyderabad': 1.5, 'Chennai': 1.3, 'Kolkata': 1.1, 'Ahmedabad': 1.0
    };
    
    const basePrice = 15000;
    const multiplier = locationMultipliers[formData.location] || 1.5;
    const pricePerSqft = basePrice * multiplier * (1 - formData.age_years * 0.005);
    const predictedPrice = Math.round(pricePerSqft * formData.area_sqft);
    
    let confidence = 70;
    if (formData.bedrooms && formData.bathrooms) confidence += 10;
    if (formData.furnishing) confidence += 8;
    if (selectedAmenities.size > 0) confidence += 5;
    if (formData.parking) confidence += 3;
    confidence = Math.min(confidence, 85); // Reduced when using fallback
    
    const variance = predictedPrice * (1 - confidence / 100) * 0.5;
    
    return {
      predictedPrice,
      minPrice: Math.round(predictedPrice - variance),
      maxPrice: Math.round(predictedPrice + variance),
      confidence,
      features: {
        location: 34, area: 28, bedrooms: 18, age: 11, other: 9
      }
    };
  }
}

// ============================================================================
// LOADING STATE
// ============================================================================

function showLoadingState() {
  loadingSpinner.classList.add('show');
  outputPlaceholder.style.display = 'none';
  resultCard.classList.remove('show');
  submitBtn.disabled = true;
}

function hideLoadingState() {
  loadingSpinner.classList.remove('show');
  submitBtn.disabled = false;
}

// ============================================================================
// DISPLAY RESULT
// ============================================================================

function displayResult(result) {
  const { predictedPrice, minPrice, maxPrice, confidence, features } = result;
  
  // Hide placeholder and show result
  outputPlaceholder.style.display = 'none';
  resultCard.classList.add('show');
  
  // Format prices
  const crorePrice = (predictedPrice / 10000000).toFixed(2);
  const minCrore = (minPrice / 10000000).toFixed(2);
  const maxCrore = (maxPrice / 10000000).toFixed(2);
  
  // Update price display
  document.getElementById('predictedPrice').textContent = 
    `₹ ${(predictedPrice / 100000).toFixed(2)}L`;
  
  document.getElementById('predictedCrore').textContent = 
    `₹ ${crorePrice} Crore`;
  
  // Update confidence
  document.getElementById('confidenceText').textContent = 
    `Range: ₹${minCrore}Cr – ₹${maxCrore}Cr`;
  
  document.getElementById('confidenceLabel').textContent = 
    `Confidence: ${confidence}%`;
  
  // Animate confidence bar
  const confidenceFill = document.getElementById('confidenceFill');
  setTimeout(() => {
    confidenceFill.style.width = confidence + '%';
  }, 100);
  
  // Update feature table
  const featureTable = document.getElementById('featureTable');
  featureTable.innerHTML = '';
  
  Object.entries(features).forEach(([feature, percentage]) => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${feature.charAt(0).toUpperCase() + feature.slice(1)}</td>
      <td>
        <span class="feature-bar" style="width: ${percentage}%;"></span>
        ${percentage}%
      </td>
    `;
    featureTable.appendChild(row);
  });
  
  console.log('✓ Result displayed');
}

// ============================================================================
// NEW PREDICTION BUTTON
// ============================================================================

document.querySelectorAll('button').forEach(btn => {
  if (btn.textContent.includes('New Prediction')) {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      
      // Reset form
      form.reset();
      sessionStorage.clear();
      selectedAmenities.clear();
      
      // Reset UI
      document.querySelectorAll('.segmented-btn.active').forEach(b => {
        b.classList.remove('active');
      });
      
      document.querySelectorAll('.pill-tag.active').forEach(tag => {
        tag.classList.remove('active');
      });
      
      if (parkingToggle) {
        parkingToggle.checked = false;
        parkingLabel.textContent = 'No';
      }
      
      // Reset sliders
      if (ageSlider) {
        ageSlider.value = 15;
        ageOutput.textContent = '15';
      }
      
      // Hide result, show placeholder
      resultCard.classList.remove('show');
      outputPlaceholder.style.display = 'flex';
      confidenceFill.style.width = '0%';
      
      console.log('✓ Form reset for new prediction');
    });
  }
});

// ============================================================================
// DOWNLOAD REPORT (mock)
// ============================================================================

document.querySelectorAll('button').forEach(btn => {
  if (btn.textContent.includes('Download Report')) {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      console.log('✓ Report download initiated');
      alert('Report generation coming soon!');
    });
  }
});

// ============================================================================
// INITIALIZATION
// ============================================================================

console.log('✓ Prediction page initialized');

// Check API availability on page load
(async () => {
  try {
    const response = await fetch('http://localhost:5000/health', { 
      method: 'GET',
      headers: { 'Accept': 'application/json' }
    });
    
    if (response.ok) {
      const data = await response.json();
      console.log('✅ Backend API is available:', data);
      
      // Show success indicator
      const statusEl = document.querySelector('.api-status');
      if (statusEl) {
        statusEl.classList.add('connected');
        statusEl.title = 'Backend API connected';
      }
    }
  } catch (error) {
    console.warn('⚠️ Backend API not available yet. Start server with: python run_api.py');
    console.warn('Error:', error.message);
    
    // Show warning indicator
    const statusEl = document.querySelector('.api-status');
    if (statusEl) {
      statusEl.classList.add('disconnected');
      statusEl.title = 'Backend API not available. Start with: python run_api.py';
    }
  }
})();
