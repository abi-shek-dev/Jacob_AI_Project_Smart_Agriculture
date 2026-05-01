// constants/theme.js
// ──────────────────────────────────────────────────────────────────────────────
// Design system tokens – all colors, fonts and spacing in one place.
// Update this file to retheme the entire app at once.

export const COLORS = {
  // Primary green palette (agriculture feel)
  primary:        "#2D6A4F",   // deep forest green
  primaryLight:   "#52B788",   // medium mint green
  primaryDark:    "#1B4332",   // dark forest
  accent:         "#95D5B2",   // soft leaf green (highlights)
  accentWarm:     "#D8F3DC",   // very light background tint

  // Status / semantic
  success:        "#40916C",
  warning:        "#F4A261",
  danger:         "#E63946",
  info:           "#4CC9F0",

  // Neutrals
  background:     "#0D1B0E",   // near-black green (dark mode)
  surface:        "#132A13",   // card surface
  surfaceElevated:"#1E3A1E",   // elevated card
  border:         "#2D4A2D",

  // Text
  textPrimary:    "#E8F5E9",
  textSecondary:  "#A5D6A7",
  textMuted:      "#6A9B6A",
  textInverse:    "#0D1B0E",

  // Chart palette (7 soil features)
  chart: [
    "#52B788", "#74C69D", "#95D5B2", "#B7E4C7",
    "#F4A261", "#E76F51", "#4CC9F0",
  ],
};

export const FONTS = {
  regular:   "System",
  bold:      "System",   // Expo uses system font by default; load custom in App.js if needed
};

export const SPACING = {
  xs:  4,
  sm:  8,
  md:  16,
  lg:  24,
  xl:  32,
  xxl: 48,
};

export const RADIUS = {
  sm:  8,
  md:  14,
  lg:  20,
  full: 999,
};

export const SHADOW = {
  small: {
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 4,
    elevation: 3,
  },
  large: {
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.35,
    shadowRadius: 10,
    elevation: 8,
  },
};
