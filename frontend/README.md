# EstateIQ - Premium Frontend Application
## Intelligent Real Estate Valuation Platform

A production-grade, premium real estate valuation web application built with **vanilla HTML, CSS, and JavaScript**. No frameworks, no templates, no compromises.

---

## 📁 Project Structure

```
frontend/
├── index.html           # Landing page with hero, features, CTAs
├── dashboard.html       # Analytics dashboard with KPIs, charts, tables
├── prediction.html      # Property valuation form with live results
├── styles.css           # Global design system & all styling
├── landing.js           # Landing page interactions & animations
├── dashboard.js         # Dashboard logic & visualizations
└── prediction.js        # Form handling, validation, predictions
```

---

## 🎨 Design System

### Colors (Dark Mode Premium)
```css
Primary Background:    #0A0A0A (near black)
Secondary Background:  #111111
Surface/Cards:         #161616
Border:               #2A2A2A
Primary Accent:       #C8A96E (warm gold)
Secondary Accent:     #8B5E3C (deep terracotta)
Text Primary:         #F0EDE8 (warm off-white)
Text Secondary:       #9A9489 (muted gray)
Success:              #2E5E32
Error:                #8B3A3A
```

### Typography
- **Headings**: Syne (700, 600 weight) — bold, architectural
- **Body**: Inter (400, 500, 600 weight) — clean, readable
- **Monospace**: JetBrains Mono — data, numbers, code
- **Base size**: 16px | Line height: 1.6

### Spacing
All spacing uses an **8px grid system**:
```
8px, 16px, 24px, 32px, 48px, 64px, 96px, 128px
```

### Border Radius
```
Buttons/Inputs: 3px (subtle, not harsh)
Cards: 4px (premium feel)
Pills/Tags: 2px (minimal)
```

### Shadows
- **Card**: `0 1px 3px rgba(0,0,0,0.4), 0 4px 16px rgba(0,0,0,0.25)`
- **Elevated**: `0 8px 32px rgba(0,0,0,0.5)`

---

## 🚀 Pages Overview

### 1. **Landing Page** (`index.html`)

The entry point showcasing EstateIQ's value proposition.

**Sections:**
- **Header/Navbar** (64px fixed)
  - Logo & wordmark
  - Navigation links (Features, Dashboard, Predict, About)
  - "Get Started" CTA button
  - Glass-morphism effect on scroll

- **Hero Section** (Full viewport height)
  - Luxury architecture background image (parallax at 0.4x scroll speed)
  - Left column: Headline, subtext, email input, trust note
  - Right column: Floating glassmorphism stat card
    - 94.2% Accuracy
    - ₹2.4Cr Average Value
    - 12,000+ Properties Analyzed
    - Live model badge with pulsing green dot
  - Animated scroll indicator

- **Trust Strip**
  - 6 partner/user logos (Prestige, Brigade, HDFC, etc.)
  - Simple text-based branding

- **Features Section** (6-column grid)
  - ML Price Engine
  - Location Intelligence
  - Market Benchmarks
  - Instant API Access
  - Power BI Integration
  - Audit-Ready Reports
  - Each with icon, title, description
  - Hover state: border color animates to gold

- **How It Works** (Timeline)
  - 3 steps with vertical dashed gold line
  - Right side: mock prediction output in monospace
  - "01 / 03", "02 / 03", "03 / 03" numbering

- **CTA Section**
  - "Start predicting today" headline
  - Primary CTA button
  - Footer with logo, tagline, nav links

**Animations:**
- Slide up + fade on scroll (IntersectionObserver)
- Staggered reveals (80ms delays)
- Number counters animate 0 → target
- Parallax background on mouse scroll
- Navbar glass effect on scroll past 80px

---

### 2. **Dashboard Page** (`dashboard.html`)

Complete analytics dashboard for viewing predictions and performance metrics.

**Layout:**
- Fixed left sidebar (240px) + main content area
- Top sticky bar with filters

**Sidebar:**
- Logo
- Navigation (Dashboard, Predictions, Analytics, Reports, Settings)
- Active state: gold left border, background tint
- User profile card (avatar, name, plan tier)

**Main Content:**
- **Top Bar**: Title, date, notification bell, user avatar
- **Filters Panel**: Location dropdown, Bedrooms, Price range, Apply/Reset buttons
- **KPI Cards** (4-column grid):
  1. Average Price: ₹1.84 Cr (+3.2% trend)
  2. Total Predictions: 12,847 (counter animated)
  3. Model Accuracy: 94.2% (with progress bar)
  4. Highest Value: ₹6.2 Cr (with location tag)

- **Charts Section** (60% / 40% split):
  - Left: Area chart "Price by Area (sq ft)"
    - Smooth curve, gradient fill
    - Grid lines, axis labels
    - Data point markers
  - Right: Horizontal bar chart "Price by Location"
    - Animated bars (staggered width animation)
    - Multiple locations with counts

- **Recent Predictions Table**
  - 8 columns: Property ID, Location, Area, Beds, Predicted, Actual, Error %, Status
  - Alternating row backgrounds
  - Success badges (green)
  - Monospace pricing values

**Interactions:**
- Filters apply/reset
- Sidebar navigation highlights active state
- Counter animations on card entering viewport
- Bar chart widths animate on scroll

---

### 3. **Prediction Page** (`prediction.html`)

Property valuation form with live results display.

**Layout:**
- Same sidebar + main content
- Two-column split (55% / 45%)

**Left Column: Input Form**
- Section label: "PROPERTY DETAILS"
- Title: "Estimate Property Value"

**Form Fields:**
1. **Area (sq ft)** — number input
2. **Location** — select dropdown (8 cities)
3. **Bedrooms** — segmented buttons (1-5BHK+)
4. **Bathrooms** — segmented buttons (1-4+)
5. **Property Age** — range slider (0-100) with live output
6. **Floor Number** — number input
7. **Furnishing Status** — segmented (Unfurnished/Semi/Fully)
8. **Parking Available** — toggle switch (CSS-only, beautiful pill shape)
9. **Amenities** — pill tag buttons (Gym, Pool, Security, Lift, Garden, Club)

**Form Validation:**
- Area: 100-50000 sq ft
- Location: required
- Bedrooms: required
- Bathrooms: required

**Right Column: Output Display**

*Before Prediction:*
- CSS house icon (geometric shapes)
- "Your prediction will appear here"

*After Prediction:*
- Big price: ₹ 1,42,00,000 (in mono)
- Crore conversion: ₹ 1.42 Crore
- Price range with confidence
- Horizontal confidence bar (animated width, gradient fill)
- Feature Importance table:
  - Location: 34%
  - Area: 28%
  - Bedrooms: 18%
  - Age: 11%
  - Other: 9%
  - Each with mini bars
- Action buttons: "Download Report" (outline), "New Prediction" (text)

**Interactions:**
- Segmented groups: click to select, toggle active state, store in sessionStorage
- Range slider: displays current value in real-time
- Toggle switch: label updates (Yes/No)
- Pill tags: click to toggle active, store selections
- Form submission:
  - Validation checks
  - Loading spinner appears (CSS rotation)
  - 1200ms simulated delay
  - Result card slides in
  - Confidence bar animates to final width
- "New Prediction": resets form, clears selections, hides results

---

## 🎬 Animations & Interactions

### Global Animations
```css
Easing: cubic-bezier(0.16, 1, 0.3, 1)
Duration: 0.5s - 0.8s
```

### Key Patterns

1. **Scroll Animations**
   - Elements slide up 24px + fade in (opacity 0 → 1)
   - Triggered by IntersectionObserver (threshold: 0.1)
   - Staggered with 80ms delays between items

2. **Parallax**
   - Hero background moves at 0.4x scroll speed
   - `transform: translateY(scrollY * 0.4)`
   - Smooth, not jarring

3. **Counter Animation**
   - KPI numbers animate 0 → target value
   - Duration: 1200ms
   - RequestAnimationFrame for smoothness
   - Triggered on intersection

4. **Hover States**
   - Buttons: translate up 2px, shadow deepens
   - Cards: border changes to gold, shadow increases
   - All transitions use design system easing

5. **Form States**
   - Segmented buttons: border/background color change
   - Toggle switch: smooth sliding
   - Range slider: thumb scales on hover
   - Focus states: gold border + subtle glow

6. **Loading**
   - Spinner: CSS rotation animation
   - Can be toggled with `.show` class

7. **Result Display**
   - Slide up + fade animation on reveal
   - Confidence bar width animates with easing
   - Feature bars remain static (no animation)

---

## 💻 JavaScript Implementation

### `landing.js`
- Navbar scroll detection (add `scrolled` class at 80px)
- Parallax effect on hero background
- IntersectionObserver for scroll animations
- Number counter animations
- CTA button navigation
- Smooth scroll for anchor links

### `dashboard.js`
- Sidebar navigation state management
- IntersectionObserver for card animations
- Counter animations for KPI cards
- Filter button logic
- Chart animation triggers
- Responsive behavior on resize

### `prediction.js`
- Segmented button group handlers
- Range slider value display
- Toggle switch label updates
- Amenity pill tag selection
- Form validation logic
- Mock API call simulation (1200ms delay)
- Result card display with animations
- Feature table population
- New prediction reset functionality

**All vanilla JS — no libraries, no frameworks.**

---

## 🔌 How to Use

### 1. **Local Development**
```bash
# Navigate to frontend directory
cd frontend/

# Open in browser
# Simple HTTP server (Python)
python -m http.server 8000

# Then visit: http://localhost:8000
```

### 2. **File Organization**
Place all 7 files in the same directory:
```
your-project/
├── index.html
├── dashboard.html
├── prediction.html
├── styles.css
├── landing.js
├── dashboard.js
└── prediction.js
```

### 3. **Navigation**
- **Landing Page** → Click "Get Started" or "Predict Price" → Prediction Page
- **Dashboard** → Click logo → Landing Page
- **Prediction Form** → Submit → See results immediately

---

## 🎯 Key Features

### ✅ **Design Excellence**
- Premium dark mode aesthetic
- Gold accent color used sparingly for maximum impact
- Consistent 8px spacing grid
- Professional typography hierarchy
- Subtle shadows (no glows or neon)

### ✅ **Performance**
- Vanilla JS (no bundle bloat)
- CSS Grid & Flexbox for layouts
- Optimized animations (60fps)
- No external dependencies
- Lightweight (< 100KB total)

### ✅ **Accessibility**
- Semantic HTML structure
- Proper heading hierarchy
- Form labels linked to inputs
- Color contrast meets WCAG standards
- Keyboard navigable

### ✅ **Responsiveness**
- Mobile-first approach
- Breakpoints: 480px, 768px, 1024px
- Sidebar adapts on mobile
- Charts scale to container
- Touch-friendly button sizes

### ✅ **Interactions**
- Smooth transitions on all hover states
- IntersectionObserver for efficient animations
- Form validation with user feedback
- Loading states for async operations
- Session storage for form data persistence

---

## 📱 Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

**Note**: CSS Grid, CSS Custom Properties, and IntersectionObserver are required.

---

## 🛠️ Customization

### Change Brand Name
```bash
# Replace "EstateIQ" with your brand name in:
# - index.html (navbar, sidebar)
# - dashboard.html (navbar, sidebar)
# - prediction.html (navbar, sidebar)
```

### Change Colors
```css
/* In styles.css, update :root variables */
--color-accent: #C8A96E;  /* Change primary gold */
--color-accent-dark: #8B5E3C;  /* Change secondary */
--color-text-primary: #F0EDE8;  /* Change text */
```

### Change Location Data
```javascript
/* In prediction.js, update location options */
const locationMultipliers = {
  'Mumbai': 2.5,
  'Bangalore': 1.8,
  // Add your cities here
};
```

### Connect Real API
```javascript
/* In prediction.js, replace simulatePrediction() */
// Remove the setTimeout mock
// Replace with actual fetch call to your backend
const response = await fetch('/api/predict', {
  method: 'POST',
  body: JSON.stringify(formData)
});
```

---

## 📊 Features Summary

| Feature | Status | Details |
|---------|--------|---------|
| Landing Page | ✅ | Hero, features, CTA |
| Dashboard | ✅ | KPIs, charts, table |
| Prediction Form | ✅ | 9 form fields, validation |
| Animations | ✅ | Scroll, counter, parallax |
| Responsive Design | ✅ | Mobile, tablet, desktop |
| Dark Mode | ✅ | Premium aesthetic |
| API Integration | ⏳ | Ready for backend connection |
| Authentication | ⏳ | Placeholder UI ready |
| PDF Export | ⏳ | Button ready, needs backend |

---

## 🚀 Next Steps

1. **Connect Backend API**
   - Replace mock functions in `prediction.js`
   - Update API endpoints in all pages

2. **Add User Authentication**
   - Implement login/signup pages
   - Protect dashboard with auth guards

3. **Database Integration**
   - Store predictions in database
   - Show prediction history in dashboard

4. **Export Functionality**
   - PDF report generation
   - CSV export from dashboard

5. **Real-time Updates**
   - WebSocket integration for live data
   - Push notifications

---

## 📝 Code Quality

- **Comments**: Major sections clearly labeled
- **Semantic HTML**: Proper use of `<section>`, `<main>`, `<nav>`, `<aside>`
- **CSS Organization**: Design tokens at top, grouped by function
- **JavaScript**: Modular, event-driven, well-commented
- **No Globals**: Functions scoped appropriately
- **Error Handling**: Validation & graceful fallbacks

---

## 📄 License

This frontend is built as part of EstateIQ — a premium real estate valuation platform.

---

## 🤝 Support

For issues or customization requests, refer to the inline code comments or consult the design specification document.

---

**Built with precision. Designed for professionals. Zero compromises.**

*EstateIQ Frontend — April 2025*
