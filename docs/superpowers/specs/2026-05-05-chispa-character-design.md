# Chispa Character — Design Spec
Date: 2026-05-05

## Overview

Add Chispa's flame mascot character as an inline SVG to `index.html`. The character anchors Screen 1 with animated presence, then appears as a small static avatar in all model chat bubbles across Screens 2–6. Screens 2–6 also gain a slim branded header with just the logo mark.

---

## 1. ChispaSVG Component

**Signature:** `ChispaSVG({ size, animated = false })`

**viewBox:** `0 0 140 160` — scales uniformly via `size` prop (width is `size * (140/160)`).

**Structure (bottom to top):**

### Flame body
- 3-tip flame path above the round base: one tall center tip, two shorter side tips
- Fill: radial gradient from center `#FDE68A` → `#FAC75A` → `#EF9F27` → outer `#e76f51`
- Stroke: `#7A2E1A`, 3px, round joins

### Round base circle
- Fill: `#FAC75A`
- Stroke: `#7A2E1A`, 3px

### Face (centered in base circle)
- **Eyes:** two large round eyes
  - White sclera circle
  - `#3D1A0A` iris circle
  - Black pupil circle
  - White shine dot, top-left quadrant
  - When `animated=true`: eyeBlink animation applied (scaleY), transform-origin at eye center
- **Eyebrows:** dark brown `#7A2E1A`, slight upward arch, 2.5px stroke
- **Smile:** small open-mouth curve, `#7A2E1A` stroke, no fill
- **Cheeks:** two round ellipses, `#F4A261`, opacity 0.5, one each side

**All stroke widths:** 2.5–3px for illustration feel.

---

## 2. CSS Keyframes (added to STYLES string)

```
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50%       { transform: translateY(-10px); }
}

@keyframes eyeBlink {
  /* Blink occupies ~5% of a 4s cycle (≈0.2s) */
  0%, 93%, 100% { transform: scaleY(1); }
  96.5%          { transform: scaleY(0.1); }
}

@keyframes orbitA {
  from { transform: rotate(0deg)   translateX(72px) rotate(0deg); }
  to   { transform: rotate(360deg) translateX(72px) rotate(-360deg); }
}
@keyframes orbitB {
  from { transform: rotate(120deg)  translateX(88px) rotate(-120deg); }
  to   { transform: rotate(480deg)  translateX(88px) rotate(-480deg); }
}
@keyframes orbitC {
  from { transform: rotate(240deg)  translateX(62px) rotate(-240deg); }
  to   { transform: rotate(600deg)  translateX(62px) rotate(-600deg); }
}
```

All animations: `ease-in-out`. No bounce. No elastic.

---

## 3. LandingCharacter Component (Screen 1 only)

Centered container, `position: relative`, `display: inline-block`.

Contents:
1. **Float wrapper div** — `animation: float 3s ease-in-out infinite` — contains `<ChispaSVG size={140} animated={true} />`
2. **Three sparkle stars** — `position: absolute`, centered at container midpoint via `top: 50%; left: 50%; marginTop/Left: -4/6/3px` (half star height/width), each a 4-point star SVG path or CSS clip, color `#E9C46A`
   - Star A: 8px, opacity 0.8, `animation: orbitA 8s ease-in-out infinite`
   - Star B: 12px, opacity 0.9, `animation: orbitB 12s ease-in-out infinite`
   - Star C: 6px, opacity 0.7, `animation: orbitC 6s ease-in-out infinite`

---

## 4. Screen 1 — Landing Layout Changes

**Character placement:** `LandingCharacter` inserted between the ✦ Chispa wordmark and the headline, centered (`textAlign: center`, `marginBottom: 32px`).

**Headline copy (replaces current):**
```
Start your AI
journey with a
spark
```
- "spark": `#e76f51`, italic (`<em>`)
- Font: Syne 800, 36px, line-height 1.1, color `#f1faee`

Existing ✦ Chispa wordmark at top-left stays as-is.

---

## 5. Bubble Component — Avatar Update (All Screens)

Replace the 10×10px orange circle dot with `<ChispaSVG size={32} />`.
- `animated=false` (default) — no blink, no float, purely static
- Vertically aligned with message bottom (`alignItems: 'flex-end'` already set)

---

## 6. ChispaHeader Component (Screens 2–6)

New shared component:
```
✦  Chispa
```
- `✦` rendered as text, 16px, `#e76f51`
- "Chispa": Syne 800, 16px, `#e76f51`
- Layout: `display: flex`, `alignItems: center`, `gap: 8px`, `padding: 16px 24px`, `borderBottom: 1px solid var(--border)`, `flexShrink: 0`

Added to the top of: `renderDiscovery`, `renderPick`, `renderWin`, `renderPill`, `renderMap`.

---

## 7. Files Changed

| File | Changes |
|---|---|
| `index.html` | Add ChispaSVG, LandingCharacter, ChispaHeader components; update Bubble; update renderLanding; add to screens 2–6; add keyframes to STYLES |

No new files. No backend changes.

---

## 8. Out of Scope

- Character on Screen 1 is the only animated instance
- No hover animations on the avatar in Bubble
- No character on euforia overlay (Screen 4 win flash)
