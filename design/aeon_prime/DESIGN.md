---
name: Aeon Prime
colors:
  surface: '#0b1326'
  surface-dim: '#0b1326'
  surface-bright: '#31394d'
  surface-container-lowest: '#060e20'
  surface-container-low: '#131b2e'
  surface-container: '#171f33'
  surface-container-high: '#222a3d'
  surface-container-highest: '#2d3449'
  on-surface: '#dae2fd'
  on-surface-variant: '#bac9cc'
  inverse-surface: '#dae2fd'
  inverse-on-surface: '#283044'
  outline: '#849396'
  outline-variant: '#3b494c'
  surface-tint: '#00daf3'
  primary: '#c3f5ff'
  on-primary: '#00363d'
  primary-container: '#00e5ff'
  on-primary-container: '#00626e'
  inverse-primary: '#006875'
  secondary: '#c0c1ff'
  on-secondary: '#1000a9'
  secondary-container: '#3131c0'
  on-secondary-container: '#b0b2ff'
  tertiary: '#e7edf5'
  on-tertiary: '#2b3137'
  tertiary-container: '#cbd1d9'
  on-tertiary-container: '#535a60'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#9cf0ff'
  primary-fixed-dim: '#00daf3'
  on-primary-fixed: '#001f24'
  on-primary-fixed-variant: '#004f58'
  secondary-fixed: '#e1e0ff'
  secondary-fixed-dim: '#c0c1ff'
  on-secondary-fixed: '#07006c'
  on-secondary-fixed-variant: '#2f2ebe'
  tertiary-fixed: '#dde3eb'
  tertiary-fixed-dim: '#c1c7cf'
  on-tertiary-fixed: '#161c22'
  on-tertiary-fixed-variant: '#41474e'
  background: '#0b1326'
  on-background: '#dae2fd'
  surface-variant: '#2d3449'
  slate-900: '#0F172A'
  slate-800: '#1E293B'
  charcoal: '#111111'
  electric-indigo: '#6366F1'
  icy-blue: '#00E5FF'
  silver-matte: '#94A3B8'
typography:
  headline-xl:
    fontFamily: Plus Jakarta Sans
    fontSize: 36px
    fontWeight: '600'
    lineHeight: 44px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 22px
    fontWeight: '500'
    lineHeight: 30px
  body-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '300'
    lineHeight: 26px
    letterSpacing: 0.01em
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '300'
    lineHeight: 22px
  label-caps:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.1em
  label-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 8px
  gutter: 24px
  margin-mobile: 20px
  container-max: 1200px
  section-gap: 64px
---

## Brand & Style

The design system embodies a **Minimalist / Sophisticated Tech** aesthetic. It shifts the narrative from a playful companion to a high-precision instrument for personal evolution. The brand personality is disciplined, elite, and surgically clean, evoking an emotional response of clarity and focused momentum.

The visual style is characterized by heavy intentional whitespace, a restrained color palette, and a "glass-on-slate" interface. It draws inspiration from premium productivity suites and high-end automotive dashboards, where every pixel serves a functional purpose. The "mischievous" brand tone is reserved strictly for copy, creating a sharp, delightful contrast against the cold, professional perfection of the UI.

## Colors

The system defaults to a **Dark Mode** experience to emphasize the "cool" and premium tech vibe. The palette is built on deep, desaturated foundations with surgical light accents.

- **Primary (Icy Blue):** Used for critical data visualizations, active states, and high-priority progress indicators.
- **Secondary (Electric Indigo):** Used for primary actions and brand-specific touchpoints.
- **Tertiary (Silver/Slate):** Used for secondary text, inactive states, and subtle UI borders.
- **Neutral (Slate 900):** The primary background color, providing a deep, stable environment for content.

Surface colors utilize varying shades of Slate to create hierarchy without relying on shadows. Neon accents should be used sparingly (less than 5% of the screen area) to maintain a sophisticated feel.

## Typography

This system uses **Plus Jakarta Sans** exclusively to maintain a cohesive, modern look. The hierarchy is established through extreme weight contrast and letter spacing rather than sheer size.

- **Headlines:** Use Semi-Bold (600) for a precise, architectural feel. Avoid Bold or Extra-Bold.
- **Body Text:** Use Light (300) weight for all long-form content to create an airy, premium editorial feel.
- **Labels:** Meta-information and small tags should use All-Caps with increased letter spacing for a technical, "HUD" aesthetic.
- **Mobile Scaling:** Large headlines scale down by 15% on mobile devices, ensuring the "clean" aesthetic is maintained without crowding small screens.

## Layout & Spacing

The layout follows a **Fixed-Grid System** on desktop, providing a structured, dashboard-like environment. On mobile, it transitions to a fluid single-column layout.

- **Rhythm:** An 8px base unit governs all dimensions. Use generous internal padding (32px+) within cards to emphasize the minimalist philosophy.
- **Desktop Grid:** A 12-column layout with wide 24px gutters. Content should be organized into modular "widgets" that align strictly to the grid.
- **Mobile Layout:** Margins are set to 20px. Elements should be stacked vertically with significant vertical "breathing room" (section-gap) between distinct functional areas.

## Elevation & Depth

Depth is conveyed through **Glassmorphism** and **Tonal Layering** rather than traditional drop shadows.

- **Surface Layers:** Use a slightly lighter slate (#1E293B) for container surfaces against the deep background (#0F172A).
- **Glass Effect:** Interactive cards and modals use a translucent background (`rgba(30, 41, 59, 0.7)`) with a `backdrop-filter: blur(12px)`.
- **Borders:** Every container must have a 1px solid border. Use a low-opacity tertiary color (`rgba(226, 232, 240, 0.1)`) to create a "ghost" outline that catches the eye without adding visual weight.
- **Interactivity:** On hover, the border opacity should increase, or the neon primary color should "trace" the edge of the element.

## Shapes

The shape language is **Precise and Geometric**. The roundedness is reduced to create a sense of professional engineering.

- **Containers & Cards:** Use a consistent 8px (rounded-md) radius.
- **Action Elements:** Buttons and input fields should follow the same 8px radius for a unified, "tooled" appearance.
- **Indicators:** Use sharp, 90-degree corners for category stripes and status markers to differentiate them from interactive elements.
- **Progress Bars:** Use flat, squared ends for a more technical appearance compared to traditional rounded bars.

## Components

### Buttons
- **Primary:** Solid Electric Indigo with white text. No shadow. 1px border of a lighter indigo.
- **Secondary:** Ghost style. 1px Silver-Matte border with transparent background.
- **Tertiary/Ghost:** Text only, All-Caps label style with a subtle hover underline.

### Cards
- Translucent Slate-800 backgrounds with 12px backdrop blur. 
- 1px "Icy Blue" top-border only for "Active" or "Legendary" items.
- Internal content should be aligned to a strict sub-grid.

### Input Fields
- Darker background than the card surface.
- 1px Silver border that transitions to Icy Blue on focus.
- Monospaced fonts for numerical inputs (e.g., XP values, timers).

### Chips & Tags
- Rectangular with 4px radius. 
- Background: `rgba(255, 255, 255, 0.05)`. 
- Text: All-Caps, 10px size, Icy Blue color.

### Progress Indicators
- Linear, 4px height. 
- Track: Deep Slate. 
- Fill: Neon Icy Blue with a subtle glow (`box-shadow: 0 0 8px rgba(0, 229, 255, 0.5)`).