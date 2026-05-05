# Chispa Character Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the Chispa flame mascot SVG to `index.html` — animated on Screen 1, static 32px avatar in all model chat bubbles, `✦ Chispa` logo header on Screens 2–6.

**Architecture:** Single-file change (`index.html`). Five new React components (`ChispaSVG`, `StarShape`, `LandingCharacter`, `ChispaHeader`) inserted after the existing `Euforia` component. `Bubble` updated to replace its 10px dot. `renderLanding` gets the character + new headline copy. `renderDiscovery` / `renderPick` / `renderWin` / `renderPill` / `renderMap` each get `<ChispaHeader />` prepended. Six CSS keyframes added to the `STYLES` string.

**Tech Stack:** React 18 (CDN/Babel standalone), inline SVG, CSS keyframe animations, no new files.

---

### Task 1: Add CSS keyframes to STYLES

**Files:**
- Modify: `index.html:35` — the last line inside the STYLES template literal

- [ ] **Step 1: Find the insertion point**

Locate this exact line in the STYLES string (around line 35):
```js
    @keyframes lineFade  { from{opacity:0;transform:translateY(5px)} to{opacity:1;transform:none} }
    `
```

- [ ] **Step 2: Insert keyframes**

Replace those two lines with:
```js
    @keyframes lineFade  { from{opacity:0;transform:translateY(5px)} to{opacity:1;transform:none} }
    @keyframes float     { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-10px)} }
    @keyframes eyeBlink  { 0%,93%,100%{transform:scaleY(1)} 96.5%{transform:scaleY(0.1)} }
    @keyframes orbitA    { from{transform:rotate(0deg)   translateX(72px) rotate(0deg)}   to{transform:rotate(360deg)   translateX(72px)  rotate(-360deg)} }
    @keyframes orbitB    { from{transform:rotate(120deg) translateX(88px) rotate(-120deg)} to{transform:rotate(480deg)  translateX(88px)  rotate(-480deg)} }
    @keyframes orbitC    { from{transform:rotate(240deg) translateX(60px) rotate(-240deg)} to{transform:rotate(600deg)  translateX(60px)  rotate(-600deg)} }
    `
```

- [ ] **Step 3: Verify no parse errors**

```bash
uvicorn server:app --reload
```
Open http://localhost:8000. Browser console must be error-free.

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "style: add float/eyeBlink/orbit keyframes for character"
```

---

### Task 2: Create ChispaSVG component

**Files:**
- Modify: `index.html` — insert after the closing `}` of `function Euforia` (around line 222)

- [ ] **Step 1: Find insertion point**

Locate the end of `function Euforia` — the closing `}` followed by a blank line before `// ── component state`. Insert the block below immediately after that closing `}`.

- [ ] **Step 2: Insert ChispaSVG**

```jsx
    // ── Chispa character SVG ─────────────────────────────────────────────────

    function ChispaSVG({ size = 140, animated = false }) {
      const uid = (React.useId ? React.useId() : 'c').replace(/[^a-z0-9]/gi, '')
      const gid = `fg${uid}`
      const h = Math.round(size * 160 / 140)
      const eyeAnim = animated ? 'eyeBlink 4s ease-in-out infinite' : 'none'
      return (
        <svg viewBox="0 0 140 160" width={size} height={h} style={{ display: 'block', overflow: 'visible' }}>
          <defs>
            <radialGradient id={gid} cx="50%" cy="40%" r="60%" fx="50%" fy="25%">
              <stop offset="0%"   stopColor="#FDE68A" />
              <stop offset="28%"  stopColor="#FAC75A" />
              <stop offset="62%"  stopColor="#EF9F27" />
              <stop offset="100%" stopColor="#e76f51" />
            </radialGradient>
          </defs>

          {/* Flame — center tip (70,8), left tip (22,50), right tip (118,50) */}
          <path
            d="M70,8 C58,22 20,36 20,50 C20,63 36,74 54,81 C59,84 63,87 70,89 C77,87 81,84 86,81 C104,74 120,63 120,50 C120,36 82,22 70,8 Z"
            fill={`url(#${gid})`}
            stroke="#7A2E1A"
            strokeWidth="3"
            strokeLinejoin="round"
          />

          {/* Base circle */}
          <circle cx="70" cy="108" r="44" fill="#FAC75A" stroke="#7A2E1A" strokeWidth="3" />

          {/* Cheeks */}
          <ellipse cx="42" cy="112" rx="10" ry="7" fill="#F4A261" opacity="0.5" />
          <ellipse cx="98" cy="112" rx="10" ry="7" fill="#F4A261" opacity="0.5" />

          {/* Left eye */}
          <g style={{ transformOrigin: '53px 101px', animation: eyeAnim }}>
            <circle cx="53" cy="101" r="11" fill="white" stroke="#7A2E1A" strokeWidth="2.5" />
            <circle cx="53" cy="101" r="7"  fill="#3D1A0A" />
            <circle cx="53" cy="101" r="3.5" fill="#1a0805" />
            <circle cx="49" cy="97"  r="2"  fill="white" />
          </g>

          {/* Right eye */}
          <g style={{ transformOrigin: '87px 101px', animation: eyeAnim }}>
            <circle cx="87" cy="101" r="11" fill="white" stroke="#7A2E1A" strokeWidth="2.5" />
            <circle cx="87" cy="101" r="7"  fill="#3D1A0A" />
            <circle cx="87" cy="101" r="3.5" fill="#1a0805" />
            <circle cx="83" cy="97"  r="2"  fill="white" />
          </g>

          {/* Eyebrows */}
          <path d="M41,87 C46,82 52,82 58,85" fill="none" stroke="#7A2E1A" strokeWidth="2.5" strokeLinecap="round" />
          <path d="M82,85 C88,82 94,82 99,87" fill="none" stroke="#7A2E1A" strokeWidth="2.5" strokeLinecap="round" />

          {/* Mouth — slight open smile */}
          <path d="M57,114 C62,124 78,124 83,114" fill="#5a2010" opacity="0.7" stroke="#7A2E1A" strokeWidth="2.5" strokeLinecap="round" />
        </svg>
      )
    }
```

- [ ] **Step 3: Temporarily render to verify shape**

In `renderLanding`, add `<ChispaSVG size={140} animated={true} />` as the first child inside the outer div. Refresh. Confirm: flame body, base circle, eyes, brows, smile, cheeks all visible. Remove temp render after confirming.

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "feat: add ChispaSVG flame mascot component"
```

---

### Task 3: Create StarShape, LandingCharacter, ChispaHeader

**Files:**
- Modify: `index.html` — insert immediately after ChispaSVG (after Task 2 code)

- [ ] **Step 1: Insert StarShape**

```jsx
    function StarShape({ size, color = '#E9C46A', opacity = 0.8 }) {
      const r = size / 2, ir = r * 0.35
      const pts = Array.from({ length: 8 }, (_, i) => {
        const a = (i * 45 - 90) * Math.PI / 180
        const rad = i % 2 === 0 ? r : ir
        return `${r + rad * Math.cos(a)},${r + rad * Math.sin(a)}`
      }).join(' ')
      return (
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} style={{ display: 'block' }}>
          <polygon points={pts} fill={color} opacity={opacity} />
        </svg>
      )
    }
```

- [ ] **Step 2: Insert LandingCharacter**

The orbit stars are absolutely positioned relative to the container. Their `top: '63%'` aligns orbits around the face center (y=101 in the 160-tall SVG ≈ 63%). `transformOrigin` centers rotation on the star itself so the counter-rotate keeps it upright.

```jsx
    function LandingCharacter() {
      const orb = (anim, sz) => ({
        position: 'absolute',
        top: '63%', left: '50%',
        marginTop: -(sz / 2), marginLeft: -(sz / 2),
        transformOrigin: `${sz / 2}px ${sz / 2}px`,
        animation: `${anim} ease-in-out infinite`,
        pointerEvents: 'none',
      })
      return (
        <div style={{ position: 'relative', width: 140, height: 160, display: 'inline-block' }}>
          <div style={{ ...orb('orbitA 8s',  8),  opacity: 0.8 }}><StarShape size={8}  /></div>
          <div style={{ ...orb('orbitB 12s', 12), opacity: 0.9 }}><StarShape size={12} /></div>
          <div style={{ ...orb('orbitC 6s',  6),  opacity: 0.7 }}><StarShape size={6}  /></div>
          <div style={{ animation: 'float 3s ease-in-out infinite', position: 'relative', zIndex: 1 }}>
            <ChispaSVG size={140} animated={true} />
          </div>
        </div>
      )
    }
```

- [ ] **Step 3: Insert ChispaHeader**

```jsx
    function ChispaHeader() {
      return (
        <div style={{
          display: 'flex', alignItems: 'center', gap: 8,
          padding: '16px 24px',
          borderBottom: '1px solid var(--border)',
          flexShrink: 0,
        }}>
          <span style={{ fontSize: 16, color: 'var(--primary)', lineHeight: 1 }}>✦</span>
          <span style={{
            fontFamily: "'Syne',sans-serif", fontWeight: 800,
            fontSize: 16, color: 'var(--primary)',
          }}>Chispa</span>
        </div>
      )
    }
```

- [ ] **Step 4: Verify orbit stars**

Temporarily add `<LandingCharacter />` in renderLanding. Confirm all three stars orbit at visibly different speeds and distances. Remove temp line.

- [ ] **Step 5: Commit**

```bash
git add index.html
git commit -m "feat: add StarShape, LandingCharacter, ChispaHeader components"
```

---

### Task 4: Update Bubble — replace dot with ChispaSVG avatar

**Files:**
- Modify: `index.html:82–87` — the model avatar dot inside `function Bubble`

- [ ] **Step 1: Find the dot**

Locate in `function Bubble` (around line 82):
```jsx
          {!user && (
            <div style={{
              width: 10, height: 10, borderRadius: '50%', background: 'var(--primary)',
              flexShrink: 0, marginBottom: 4,
            }} />
          )}
```

- [ ] **Step 2: Replace with ChispaSVG avatar**

```jsx
          {!user && (
            <div style={{ flexShrink: 0, marginBottom: 2 }}>
              <ChispaSVG size={32} />
            </div>
          )}
```

- [ ] **Step 3: Verify**

Run the full flow to Screen 2. Chispa's messages should show the 32px character face. No blink animation — `animated` defaults to `false`.

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "feat: replace bubble avatar dot with 32px ChispaSVG"
```

---

### Task 5: Update renderLanding — character + headline

**Files:**
- Modify: `index.html:592–598` — the `<h1>` block in renderLanding

- [ ] **Step 1: Find the headline**

Locate in `renderLanding` (around line 592):
```jsx
          <h1 style={{
            fontFamily: "'Syne',sans-serif", fontWeight: 800,
            fontSize: 'clamp(30px, 8vw, 40px)', color: 'var(--text)',
            lineHeight: 1.15, marginBottom: 20,
          }}>
            Your first win with AI.<br />20 minutes.
          </h1>
```

- [ ] **Step 2: Replace with character + new headline**

```jsx
          <div style={{ textAlign: 'center', marginBottom: 28 }}>
            <LandingCharacter />
          </div>

          <h1 style={{
            fontFamily: "'Syne',sans-serif", fontWeight: 800,
            fontSize: 36, color: 'var(--text)',
            lineHeight: 1.1, marginBottom: 20,
          }}>
            Start your AI<br />
            journey with a<br />
            <em style={{ color: 'var(--primary)', fontStyle: 'italic' }}>spark</em>
          </h1>
```

- [ ] **Step 3: Verify Screen 1**

Check:
- `LandingCharacter` appears centered above the headline
- Float animation: character bobs up/down
- Orbit stars: 3 stars at different speeds/distances
- Eye blink: fires every ~4s
- Headline reads "Start your AI / journey with a / *spark*" with spark in `#e76f51` italic
- ✦ Chispa wordmark still at top-left (untouched)
- Page scrolls correctly on mobile viewport in DevTools

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "feat: add character to landing + update headline copy"
```

---

### Task 6: Add ChispaHeader to Screens 2–6

**Files:**
- Modify: `index.html` — renderDiscovery (~641), renderPick (~666), renderWin (~723), renderPill (~820), renderMap (~892)

#### renderDiscovery (already in a fragment `<>`)

- [ ] **Step 1: Prepend ChispaHeader**

Find:
```jsx
      const renderDiscovery = () => (
        <>
          <div style={{ flex: 1, overflowY: 'auto', padding: '24px 24px 8px' }}>
```
Replace with:
```jsx
      const renderDiscovery = () => (
        <>
          <ChispaHeader />
          <div style={{ flex: 1, overflowY: 'auto', padding: '24px 24px 8px' }}>
```

#### renderPick (opens with a bare `<div>` — needs fragment wrapper)

- [ ] **Step 2: Wrap and prepend**

Find:
```jsx
      const renderPick = () => (
        <div style={{ flex: 1, overflowY: 'auto', padding: '40px 24px 32px' }}>
```
Replace the opening with:
```jsx
      const renderPick = () => (
        <>
          <ChispaHeader />
          <div style={{ flex: 1, overflowY: 'auto', padding: '40px 24px 32px' }}>
```
Then find the single closing `</div>` of renderPick (the one that closes the outer div) and change it to:
```jsx
          </div>
        </>
```

#### renderWin (already in a fragment `<>`)

- [ ] **Step 3: Prepend ChispaHeader before the use-case pill header div**

Find:
```jsx
      const renderWin = () => (
        <>
          {/* Use case pill header */}
          <div style={{
```
Replace with:
```jsx
      const renderWin = () => (
        <>
          <ChispaHeader />
          {/* Use case pill header */}
          <div style={{
```

#### renderPill (opens with a bare `<div>` — needs fragment wrapper)

- [ ] **Step 4: Wrap and prepend**

Find:
```jsx
      const renderPill = () => (
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', padding: '40px 24px 48px', overflowY: 'auto' }}>
```
Replace the opening with:
```jsx
      const renderPill = () => (
        <>
          <ChispaHeader />
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', padding: '40px 24px 48px', overflowY: 'auto' }}>
```
Find the closing `</div>` of renderPill and change it to:
```jsx
          </div>
        </>
```

#### renderMap (opens with a bare `<div>` — needs fragment wrapper)

- [ ] **Step 5: Wrap and prepend**

Find:
```jsx
      const renderMap = () => (
          <div style={{ flex: 1, overflowY: 'auto', padding: '40px 24px 48px' }}>
```
Replace with:
```jsx
      const renderMap = () => (
        <>
          <ChispaHeader />
          <div style={{ flex: 1, overflowY: 'auto', padding: '40px 24px 48px' }}>
```
Find the closing `</div>` of renderMap and change it to:
```jsx
          </div>
        </>
```

- [ ] **Step 6: Run full flow and verify**

Click through all 6 screens. Confirm:
- Screen 1: no header (correct — character is the identity anchor)
- Screens 2–6: `✦ Chispa` header at top, 16px Syne 800

- [ ] **Step 7: Commit**

```bash
git add index.html
git commit -m "feat: add ChispaHeader to screens 2–6"
```

---

### Task 7: Final QA + push

- [ ] **Step 1: Full visual QA checklist**

Run through the complete session flow:

Screen 1:
- [ ] Character centered above headline, bobbing (float animation)
- [ ] 3 orbit stars visible at different speeds/radii
- [ ] Eye blink fires ~every 4s
- [ ] Headline: "Start your AI / journey with a / *spark*" — spark in `#e76f51` italic
- [ ] ✦ Chispa wordmark top-left unchanged
- [ ] Paragraph and form below headline unchanged

Screen 2 (Discovery):
- [ ] `✦ Chispa` header at top
- [ ] 32px character avatar left of each Chispa message bubble
- [ ] No animations on avatar

Screens 3–6:
- [ ] `✦ Chispa` header present on each
- [ ] 32px avatar in Bubble on all chat screens

All screens:
- [ ] Browser console: no errors
- [ ] Mobile (375px DevTools): no horizontal overflow, character fits within viewport

- [ ] **Step 2: Push**

```bash
git push
```
