# Styling Changes - Lifeblood Australia Theme

## Summary
Updated the UI styling to match the Australian Red Cross Lifeblood branding with a comprehensive color palette including red, orange, and pastel green colors that reflect the Lifeblood brand identity.

## Color Palette Changes

### Primary Colors
- **Lifeblood Red**: `#E31837` (Primary brand color - headers, CTAs)
- **Dark Red**: `#C20E2F` (Hover states, gradients)

### Secondary Colors  
- **Lifeblood Orange**: `#FF6F40` (Warnings, alerts, information)
- **Dark Orange**: `#E65F35` (Hover states for orange elements)
- **Light Orange Background**: `#FFF4EF` (Backgrounds for warnings)
- **Orange Text**: `#B34A1F` (Text on light orange backgrounds)

### Success/Action Colors
- **Lifeblood Green**: `#7FCC72` (Success states, add buttons, positive actions)
- **Dark Green**: `#6BB862` (Hover states for green elements)
- **Light Green Background**: `#ecfdf5` (Success message backgrounds)

### Previous Colors (Replaced)
- **Old Blue**: `#3498db`, `#2980b9` → Now Red
- **Old Purple Gradient**: `#667eea` to `#764ba2` → Now Red Gradient
- **Old Green**: `#28a745`, `#218838`, `#059669`, `#10b981` → Now Lifeblood Green `#7FCC72`
- **Old Orange**: `#f59e0b`, `#fef3c7` → Now Lifeblood Orange `#FF6F40`

## Component Changes

### 1. App Header
- Background: Changed from dark blue (`#2c3e50`) to Lifeblood red (`#E31837`)
- Maintains white text for contrast

### 2. Headings and Titles
- H2 headings: Changed from dark blue to Lifeblood red
- Section titles: Updated border colors from blue to red

### 3. Buttons
- **Primary buttons** (Run Simulation, etc.):
  - Background: Blue → Lifeblood red (#E31837)
  - Hover: Darker blue → Darker red (#C20E2F)
- **Add/Success buttons**:
  - Background: Old green (#28a745) → Lifeblood green (#7FCC72)
  - Hover: Old dark green (#218838) → Dark green (#6BB862)
- **Guide buttons**: Updated gradient from purple to red
- **Delete/Remove buttons**: Maintained red for negative actions

### 4. Form Elements
- Focus states: Blue border and shadow → Red border and shadow
- Input highlights: Updated to use red theme
- Border accents: Changed from blue to red

### 5. Cards and Panels
- Border left accents: Blue → Red
- Device/flow config cards: Blue accent → Red accent
- Stat cards: Blue border → Red border

### 6. Progress and Status Elements
- Progress bars: 
  - Low utilization: Old green (#10b981) → Lifeblood green (#7FCC72)
  - Medium utilization: Old orange (#f59e0b) → Lifeblood orange (#FF6F40)
  - High utilization: Red (maintained)
- KPI sections: Purple gradient → Red gradient
- Info badges: Blue background → Light red background
- Warning badges: Old orange → Lifeblood orange

### 7. Modal Dialogs
- Scenario Manager: Purple gradient header → Red gradient header
- Deadlock Modal: Blue accents → Red accents
- Quick Reference: Blue theme → Red theme

### 8. Interactive Elements
- Hover effects: Blue highlights → Red highlights
- Active states: Blue → Red
- Selection indicators: Blue → Red

### 9. Gradients
All gradients updated:
- `linear-gradient(135deg, #667eea 0%, #764ba2 100%)` 
- → `linear-gradient(135deg, #E31837 0%, #C20E2F 100%)`

### 10. Animations
- Pulse effects: Updated shadow colors from blue to red
- Highlight animations: Blue glow → Red glow

## Files Modified
1. `/ui/src/App.css` - Main application styles (80+ color changes)
   - Updated green colors: `#28a745`, `#218838` → `#7FCC72`, `#6BB862`
   - Updated orange colors: `#f59e0b`, `#fef3c7` → `#FF6F40`, `#FFF4EF`
2. `/ui/src/components/ScenarioManager.css` - Scenario management UI (8 color changes)
   - Updated copy button green colors
3. `/ui/src/components/DeadlockModal.css` - Error modal styling (6 color changes)
   - Updated warning/step badge orange colors
4. `/ui/src/components/ConfigForm.tsx` - Validation styling (6 color changes)
   - Updated success green and warning orange colors
5. `/ui/src/components/Results.tsx` - Utilization bar colors (3 color changes)
   - Updated utilization bar gradient colors
6. `/ui/index.html` - Updated page title to "Platelet Pooling Simulator | Lifeblood"

## Testing Notes
The styling changes are purely cosmetic and do not affect functionality. All interactive elements maintain the same behavior with updated visual appearance aligned with Lifeblood branding.

## Accessibility
- Maintained proper color contrast ratios for readability
- Red color (#E31837) on white background meets WCAG AA standards
- White text on red background maintains sufficient contrast
- All interactive elements remain clearly distinguishable

## Browser Compatibility
Changes use standard CSS properties compatible with all modern browsers. No breaking changes introduced.
