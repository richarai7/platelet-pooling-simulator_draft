# Styling Changes - Lifeblood Australia Theme

## Summary
Updated the UI styling to match the Australian Red Cross Lifeblood branding, replacing the previous blue color scheme with Lifeblood's signature red theme.

## Color Palette Changes

### Primary Colors
- **Old Blue**: `#3498db` (Sky Blue)
- **New Red**: `#E31837` (Lifeblood Red)

### Secondary Colors  
- **Old Blue**: `#2980b9` (Darker Blue)
- **New Red**: `#C20E2F` (Dark Red)

### Accent Colors
- **Old Purple Gradient**: `#667eea` to `#764ba2`
- **New Red Gradient**: `#E31837` to `#C20E2F`

### Supporting Colors
- **Old Blue Tints**: `#3b82f6`, `#2563eb`, `#1e40af`
- **New Red Tints**: `#E31837`, `#C20E2F`, various red shades

## Component Changes

### 1. App Header
- Background: Changed from dark blue (`#2c3e50`) to Lifeblood red (`#E31837`)
- Maintains white text for contrast

### 2. Headings and Titles
- H2 headings: Changed from dark blue to Lifeblood red
- Section titles: Updated border colors from blue to red

### 3. Buttons
- **Primary buttons** (Run Simulation, etc.):
  - Background: Blue → Lifeblood red
  - Hover: Darker blue → Darker red
- **Guide buttons**: Updated gradient from purple to red
- **Action buttons**: Maintained green/red for positive/negative actions

### 4. Form Elements
- Focus states: Blue border and shadow → Red border and shadow
- Input highlights: Updated to use red theme
- Border accents: Changed from blue to red

### 5. Cards and Panels
- Border left accents: Blue → Red
- Device/flow config cards: Blue accent → Red accent
- Stat cards: Blue border → Red border

### 6. Progress and Status Elements
- Progress bars: Blue/green gradient → Red gradient
- KPI sections: Purple gradient → Red gradient
- Info badges: Blue background → Light red background

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
1. `/ui/src/App.css` - Main application styles (64 color changes)
2. `/ui/src/components/ScenarioManager.css` - Scenario management UI (6 color changes)
3. `/ui/src/components/DeadlockModal.css` - Error modal styling (4 color changes)
4. `/ui/index.html` - Updated page title to "Platelet Pooling Simulator | Lifeblood"

## Testing Notes
The styling changes are purely cosmetic and do not affect functionality. All interactive elements maintain the same behavior with updated visual appearance aligned with Lifeblood branding.

## Accessibility
- Maintained proper color contrast ratios for readability
- Red color (#E31837) on white background meets WCAG AA standards
- White text on red background maintains sufficient contrast
- All interactive elements remain clearly distinguishable

## Browser Compatibility
Changes use standard CSS properties compatible with all modern browsers. No breaking changes introduced.
