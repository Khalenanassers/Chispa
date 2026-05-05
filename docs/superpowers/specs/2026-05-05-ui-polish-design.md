# UI Polish & Landing Animations — Design Spec
Date: 2026-05-05

## Overview

Visual redesign pass on `index.html`. No JS logic, API calls, or screen transitions changed. Covers Screen 1 polish, bubble redesign, pick card micro-interaction, pill screen consistency, progress indicators, map CTA, and a Typewriter fix.

---

## 1. Screen 1 — Landing (Visual)

### SVG Star Wordmark
Replace the `✦` text character in the landing wordmark with an inline SVG star path (20px, `#e76f51`):
```html
<svg width="20" height="20" viewBox="-12 -12 24 24">
  <path d="M0,-11 L2.75,-2.75 L11,0 L2.75,2.75 L0,11 L-2.75,2.75 L-11,0 L-2.75,-2.75 Z" fill="#e76f51"/>
</svg>
```
Same SVG used in ChispaHeader on Screens 2–6 (at 16px).

### Input
- `borderRadius`: 12px → 16px
- bg `#1e363f`, border `1px solid #3d5a66`, placeholder color `#a8b8bc` (already token-correct — just confirm borderRadius)

### CTA Button
- Text: "Let's Go ⚡"
- bg: `#e76f51`, text color: `#264653` (dark), border-radius: 16px, height: 56px
- Font: Syne 800, 18px
- Disabled state: keep bg `#e76f51` always, add `opacity: 0.5` when `!input.trim()` instead of swapping to `var(--surface)` bg

### fadeSlideUp Animation
New keyframe added to STYLES:
```css
@keyframes fadeSlideUp {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}
```
Applied inline via `animation` style prop:
- h1: `fadeSlideUp 0.5s ease-in-out 0.2s both`
- input wrapper/form: `fadeSlideUp 0.5s ease-in-out 0.4s both`
- button: `fadeSlideUp 0.5s ease-in-out 0.5s both`

Use `animationFillMode: 'both'` so elements start invisible before delay fires.

### Mobile Character Size
`LandingCharacter` receives `size` from parent based on `window.innerHeight`:
- `innerHeight < 700`: size = 110
- Otherwise: size = 140

Implement via `useState` + `useEffect` (one-time read on mount, no resize listener needed). Pass `size` prop to `LandingCharacter` and forward to `ChispaSVG`.

---

## 2. Chat Bubbles — All Screens

### Model bubble
- bg: `#1e363f` (was `var(--surface)` — same value, explicit)
- text: `#f1faee`
- border-radius: `4px 16px 16px 16px`
- font-size: 16px, line-height: 1.6
- Keep existing border: `1px solid var(--border)`

### User bubble
- bg: `#e76f51`
- text: `#264653`
- border-radius: `16px 4px 16px 16px`
- Remove existing border (user bubble had none — confirm)

### Loading typing indicator
Replace the inline 10px dot + Dots component row in `renderDiscovery` and `renderWin` with:
```jsx
<div style={{ display: 'flex', gap: 8, alignItems: 'flex-end', marginBottom: 12 }}>
  <div style={{ flexShrink: 0, marginBottom: 2 }}>
    <ChispaSVG size={24} />
  </div>
  <div style={{ padding: '8px 14px', background: '#1e363f', borderRadius: '4px 16px 16px 16px', border: '1px solid var(--border)' }}>
    <Dots />
  </div>
</div>
```

### Loading dots (Dots component)
- Dot size: 8px (was 8px — confirm)
- Color: `#e76f51` (was `var(--primary)` — same)
- Stagger: 0.2s between each dot (already implemented — confirm timing)

---

## 3. Pick Cards — Hover Micro-Interaction

Add to existing card hover handling in `renderPick`:
```js
onMouseEnter: boxShadow = '0 4px 16px rgba(0,0,0,0.3)', transform includes translateY(-2px)
onMouseLeave: restore original shadow/transform
```
- Transition: `box-shadow 0.2s ease-in-out, transform 0.2s ease-in-out`
- Only fire when `!selectedCard` (card is still selectable)

---

## 4. Pill Screen — SVG Star Replaces Emoji

Replace `💡 What just happened:` label with:
```jsx
<span style={{ display: 'inline-flex', alignItems: 'center', gap: 6, ... }}>
  <svg width="14" height="14" viewBox="-12 -12 24 24">
    <path d="M0,-11 L2.75,-2.75 L11,0 L2.75,2.75 L0,11 L-2.75,2.75 L-11,0 L-2.75,-2.75 Z" fill="#e9c46a"/>
  </svg>
  What just happened:
</span>
```
Color `#e9c46a` (matches `--highlight`, pill-only context — intentional).

---

## 5. Progress Dots — Screens 2–5

New `ProgressDots({ screen })` component:
- Fixed position: `bottom: 16px`, centered horizontally
- 6 dots, 8px diameter, gap 6px
- Active screen dot: `#e76f51`, rest: `#3d5a66`
- Screen → active dot index mapping:
  - `discovery` → 0
  - `pick` → 1
  - `win` → 2
  - `pill` → 3
  - (map screen: no dots rendered)
- `pointerEvents: none`, `zIndex: 10`

Add `<ProgressDots screen={screen} />` to the main render return, rendered conditionally when `screen !== 'landing' && screen !== 'map'`.

---

## 6. Map Screen — Primary Save CTA

Replace current "Save my map" secondary button styling with:
- Full-width, bg `#e76f51`, text `#264653`, Syne 800
- border-radius: 12px, padding: 15px
- Same onClick handler — no logic change

---

## 7. ChispaHeader — SVG Star + Font Size

- Replace `✦` span with 16px SVG star (same path, fill `#e76f51`)
- "Chispa" span: fontSize 16px → 18px

---

## 8. Typewriter Key Fix

At every `<Bubble>` call site (renderDiscovery, renderWin, renderPill, renderMap), confirm `key={m.id}` is set on each Bubble. This ensures Typewriter unmounts + remounts per message, preventing the reset-on-re-render bug.

Current code already uses `key={m.id}` at Bubble call sites — verify this is present everywhere and that `msg.id` is always unique (uses `Date.now() + Math.random()` — confirm).

---

## 9. Files Changed

| File | Changes |
|---|---|
| `index.html` | All of the above — visual only, no logic |

No new files. No backend changes.

---

## 10. Out of Scope

- Flame mascot and its orbit/float/eyeBlink animations — untouched
- Logo mark float/orbit animations — not added (user decision)
- All JS state, API calls, stage routing — untouched
- Euforia overlay styling — untouched
