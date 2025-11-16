# Chat Node Visual Design Guide

## Node Appearance

### Default State (Not Configured)
```
┌─────────────────────────────────────┐
│  ⚪ Chat Input                      │
│     Manual Trigger                  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │  Click to configure message   │  │ (dashed border)
│  └───────────────────────────────┘  │
│                                     │
│  🟢 Ready for input                 │
└─────────────────────────────────────┘
```

### Configured State
```
┌─────────────────────────────────────┐
│  💬 Chat Input                      │
│     Manual Trigger                  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │ "Hello! How can I help you    │  │ (solid border)
│  │  today?"                      │  │
│  └───────────────────────────────┘  │
│                                     │
│  🟢 Ready for input                 │
└─────────────────────────────────────┘
```

### Selected State (Scale 1.05x)
```
┌═════════════════════════════════════┐
║  💬 Chat Input                      ║
║     Manual Trigger                  ║ (BOLD CYAN BORDER)
║                                     ║ (SHADOW EFFECT)
║  ┌───────────────────────────────┐  ║
║  │ "Hello! How can I help you    │  ║
║  │  today?"                      │  ║
║  └───────────────────────────────┘  ║
║                                     ║
║  🟢 Ready for input                 ║
└═════════════════════════════════════┘
```

## Configuration Panel

### General Tab
```
╔════════════════════════════════════════╗
║ Configure chatNode                     ║
╠════════════════════════════════════════╣
║ [General] [Parameters] [Advanced]      ║
╠════════════════════════════════════════╣
║                                        ║
║ Label                                  ║
║ ┌────────────────────────────────────┐ ║
║ │ Chat Input                         │ ║
║ └────────────────────────────────────┘ ║
║                                        ║
║ 💬 Welcome Message                     ║
║ ┌────────────────────────────────────┐ ║
║ │ Enter the message that will be     │ ║
║ │ displayed when workflow starts...  │ ║
║ │                                    │ ║
║ │                                    │ ║
║ └────────────────────────────────────┘ ║
║ 💡 This message will be shown at the   ║
║    start of workflow execution.        ║
║                                        ║
║ ┌────────────────────────────────────┐ ║
║ │ 💬 How Chat Input Works            │ ║
║ │                                    │ ║
║ │ 1. Your welcome message is         │ ║
║ │    displayed to the user           │ ║
║ │                                    │ ║
║ │ 2. User provides input through     │ ║
║ │    the execution dialog            │ ║
║ │                                    │ ║
║ │ 3. Input is available as           │ ║
║ │    {{ $json.message }}             │ ║
║ └────────────────────────────────────┘ ║
║                                        ║
║ ┌────────────────────────────────────┐ ║
║ │ Example: If you set "Hello! How    │ ║
║ │ can I help you today?" as the      │ ║
║ │ welcome message...                 │ ║
║ └────────────────────────────────────┘ ║
║                                        ║
║ Description                            ║
║ ┌────────────────────────────────────┐ ║
║ │                                    │ ║
║ └────────────────────────────────────┘ ║
║                                        ║
║                     [Cancel] [Save]    ║
╚════════════════════════════════════════╝
```

## Color Palette

### Light Mode
- **Background**: Gradient from Cyan-50 to Blue-50
- **Border**: Cyan-300 (default), Cyan-400 (hover), Cyan-500 (selected)
- **Icon Badge**: Cyan-500 background, white icon
- **Message Box**: White/60 with Cyan-200 border
- **Placeholder Box**: White/40 with dashed Cyan-300 border
- **Status Dot**: Cyan-500 with pulse animation
- **Text Primary**: Gray-800
- **Text Secondary**: Gray-500

### Dark Mode
- **Background**: Gradient from Gray-800 to Gray-900
- **Border**: Cyan-600 (default), Cyan-500 (hover), Cyan-500 (selected)
- **Icon Badge**: Cyan-600 background, white icon
- **Message Box**: Gray-900/40 with Cyan-800 border
- **Placeholder Box**: Gray-900/30 with dashed Cyan-700 border
- **Status Dot**: Cyan-500 with pulse animation
- **Text Primary**: Gray-100
- **Text Secondary**: Gray-400

## Animations

### 1. Pulse Animation (Status Dot)
```
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
```
**Duration**: Continuous
**Timing**: ease-in-out

### 2. Scale Transition (Selection)
```
Transform: scale(1.05)
Transition: all 200ms ease
```

### 3. Border Transition (Hover)
```
Border-color: cyan-300 → cyan-400
Transition: all 150ms ease
```

### 4. Shadow Transition
```
Shadow: none → shadow-cyan-200
Transition: all 200ms ease
```

## Spacing & Sizing

### Node Dimensions
- **Min Width**: 200px
- **Padding**: 20px (5 units)
- **Border Radius**: 12px (xl)
- **Border Width**: 2px

### Icon Badge
- **Size**: 32px × 32px
- **Border Radius**: 8px (lg)
- **Icon Size**: 18px (4.5 units)

### Handle (Connection Points)
- **Size**: 12px × 12px (3 units)
- **Border**: 2px solid white/gray-800

### Text Sizing
- **Label**: 14px (text-sm), font-semibold
- **Subtitle**: 12px (text-xs)
- **Message Preview**: 12px (text-xs)
- **Status**: 12px (text-xs), font-medium

### Spacing
- **Header Gap**: 10px (2.5 units)
- **Section Margin**: 12px (3 units)
- **Footer Padding**: 8px (2 units)

## Typography

### Font Weights
- **Label**: 600 (semibold)
- **Status**: 500 (medium)
- **Subtitle**: 400 (normal)
- **Message**: 400 (normal)

### Line Heights
- **Label**: 1.2
- **Message**: 1.5 (relaxed)
- **Status**: 1

## Interaction States

### 1. Default (Idle)
- Border: Cyan-300
- Background: Gradient normal
- Shadow: Standard lg
- Scale: 1.0

### 2. Hover
- Border: Cyan-400 (darker)
- Background: Same gradient
- Shadow: Same
- Scale: 1.0
- Cursor: Move (for dragging)

### 3. Selected
- Border: Cyan-500 (darkest)
- Background: Same gradient
- Shadow: Cyan-200 glow
- Scale: 1.05 (larger)

### 4. Dragging
- Opacity: 0.6
- Scale: 0.95
- Cursor: Grabbing

### 5. Connecting (Source/Target)
- Handle Highlight: Cyan-600
- Handle Size: 14px (slightly larger)

## Responsive Behavior

### Desktop (> 1024px)
- Full size display
- All elements visible
- Hover effects enabled

### Tablet (768px - 1024px)
- Same as desktop
- Touch-optimized hit areas

### Mobile (< 768px)
- Maintain min-width
- Touch-friendly spacing
- No hover effects
- Tap to select

## Accessibility

### ARIA Labels
```html
<div role="button" aria-label="Chat Input Node">
  <div role="img" aria-label="Chat icon"></div>
  <div role="status">Ready for input</div>
</div>
```

### Keyboard Navigation
- **Tab**: Focus node
- **Enter/Space**: Open configuration
- **Arrow Keys**: Move node (when selected)
- **Delete**: Remove node

### Screen Reader Announcements
- "Chat Input Node"
- "Manual trigger for workflow"
- "Ready for input status"
- "Has welcome message configured" / "No message configured"

## Implementation Checklist

Visual Elements:
- [x] Gradient background (cyan to blue)
- [x] Icon badge with circular background
- [x] Dual-line header (name + subtitle)
- [x] Message preview box
- [x] Placeholder box (dashed border)
- [x] Status indicator with pulse
- [x] Enhanced handles with borders

Interactions:
- [x] Scale effect on selection
- [x] Border color change on hover
- [x] Shadow effect on selection
- [x] Smooth transitions (200ms)

Configuration:
- [x] Welcome message textarea
- [x] Helper text and guidance
- [x] "How It Works" section
- [x] Example usage section
- [x] Real-time preview update

## Quick Reference

| Element | Color (Light) | Color (Dark) |
|---------|---------------|--------------|
| Background | Cyan-50 to Blue-50 | Gray-800 to Gray-900 |
| Border Default | Cyan-300 | Cyan-600 |
| Border Hover | Cyan-400 | Cyan-500 |
| Border Selected | Cyan-500 | Cyan-500 |
| Icon Badge BG | Cyan-500 | Cyan-600 |
| Status Dot | Cyan-500 | Cyan-500 |
| Text Primary | Gray-800 | Gray-100 |
| Text Secondary | Gray-500 | Gray-400 |

---

**Design Philosophy**: Clean, professional, intuitive - inspired by n8n's excellent UX principles.
