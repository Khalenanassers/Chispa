# Chispa — UI/UX Brief
**Version:** 1.0 · April 30, 2026
**Design principle:** Every screen has one emotional job. Design for that job first.

---

## DESIGN SYSTEM

### Colors — Sunset Boulevard Theme
*Source: Theme Factory · Sunset Boulevard*
*Rationale: Warm, human, energetic — matches Chispa's emotional contract. Doesn't read as "AI/tech". The fire palette maps directly to the spark metaphor.*

| Token | Hex | Usage |
|---|---|---|
| Background | `#264653` | All screens — deep purple, dark but warm |
| Surface | `#1e363f` | Cards, input areas — slightly lighter than bg |
| Primary | `#e76f51` | CTAs, Chispa name, key moments — Burnt Orange |
| Accent | `#f4a261` | Hover states, secondary actions — Coral |
| Highlight | `#e9c46a` | Euforia moment, Pill card, win confirmation — Warm Sand |
| Text Primary | `#f1faee` | All body text — warm cream, not cold white |
| Text Secondary | `#a8b8bc` | Hints, labels — muted warm grey |
| Border | `#3d5a66` | Card borders — subtle, warm |

**Color rules for Chispa:**
- Burnt Orange is the primary action color — buttons, name, key moments
- Warm Sand `#e9c46a` is reserved for euforia and pill only — do not use elsewhere
- The background must never feel cold — `#264653` is purple-based, not blue-black
- Never use Khalena's teal `#00F0C0` anywhere in Chispa

### Typography
- Headlines: **DejaVu Sans Bold** (Theme Factory standard) — or Syne 800 if web fonts available
- Body: **DejaVu Sans** — clean, readable, universally available
- Labels: IBM Plex Mono 400 — for output cards and code-adjacent content only

### Spacing
- Mobile-first. Max width 480px centered.
- Padding: 24px horizontal on all screens.
- Card border-radius: 12px.

### Motion
- All transitions: 300ms ease-in-out
- Cards enter from bottom (translateY 20px → 0)
- Pill card: pulse animation on entry (scale 1.0 → 1.02 → 1.0)
- Win output: fade in line by line (50ms stagger)

---

## SCREEN 1 — LANDING
**Emotional job:** Reduce fear. Create safety. Make starting feel small.

**What the user sees:**
- Chispa logo mark (Burnt Orange spark icon + "Chispa" in Syne)
- Headline: **"Your first win with AI. 20 minutes."**
- Subtext: "Tell me what you do. I'll show you something useful — right now. No account. No jargon. No pressure."
- Single text input: placeholder "I work as a..."
- CTA button: "Let's go →" (Burnt Orange `#e76f51`, full width)

**Design rules:**
- No menu. No nav. No options. Nothing to click except the input.
- No explanation of what Chispa is on this screen. Trust is built by doing, not reading.
- No sign-up. No email. Zero friction.

**Microcopy note:**
The subtext must not say "I'll teach you AI." It says "I'll show you something useful." Different emotional contract.

**Entry point note:**
Rosa arrives via a shared link — HR briefing, WhatsApp group, union newsletter. She has never heard of Chispa before. The landing screen has 3 seconds to earn trust. No logo explanations. No feature lists. One question. One button.

---

## SCREEN 2 — DISCOVERY (Conversational)
**Emotional job:** Make the user feel heard and understood fast.

**What the user sees:**
- Chat-style layout. Chispa messages on left (Burnt Orange avatar dot). User messages on right.
- Chispa's opening message animates in word by word (typewriter, 30ms per word).
- Input bar fixed at bottom. Send button = Burnt Orange arrow.

**Design rules:**
- Only show the last 3–4 message pairs. Don't scroll backwards.
- Chispa's messages: cream text on `#1e363f` card. Rounded corners left.
- User's messages: coral background `#c25240`. Rounded corners right.
- No timestamps. No read receipts. No noise.
- Loading state: three burnt orange dots pulsing while Gemma 4 processes.

**Transition to Screen 3:**
After Gemma 4 returns the 3 use cases, the chat fades out and 3 cards slide up from the bottom.

---

## SCREEN 3 — THE 3 OPTIONS (Pick)
**Emotional job:** Make choosing feel exciting, not overwhelming.

**What the user sees:**
- Small header text: "Here's what we can do right now:"
- 3 cards, stacked vertically, each containing:
  - Use case label (large, Syne, Burnt Orange `#e76f51`)
  - One sentence description (IBM Plex Sans, secondary color)
  - Tap anywhere on card to select
- No back button on this screen.

**Design rules:**
- Cards animate in sequentially (150ms stagger).
- On hover/tap: card border turns Burnt Orange `#e76f51`, slight scale up (1.02).
- Only one card selectable. Once tapped, other cards fade to 40% opacity.
- Selected card: Burnt Orange border, Burnt Orange checkmark top-right.
- After 800ms: selected card expands, others disappear, transition to Screen 4.

**Microcopy note:**
No "Next" button. The tap IS the action. Remove all unnecessary confirmation steps.

---

## SCREEN 4 — THE WIN (Guided Task)
**Emotional job:** Build momentum. Make them feel capable. Deliver the euforia moment.

**What the user sees — Phase A (Input collection):**
- Chispa message asking for task details (from Stage 3 prompt)
- Chat input at bottom
- Header shows selected use case as a pill tag (e.g. "✦ Write emails faster")

**What the user sees — Phase B (Output display):**
- Chispa message: "Here it is:"
- Output card: cream text `#f1faee` on `#1e363f`, slightly larger font, generous padding
- Output text fades in line by line
- Below output: two buttons
  - "✓ This is great" (Burnt Orange `#e76f51`, primary)
  - "✗ Fix something" (ghost button, secondary)

**Design rules — Phase B:**
- The output card is the most important element on screen. Give it space.
- No other UI elements compete with it.
- Line-by-line fade creates anticipation — do not skip this animation.
- "✓ This is great" must feel like a celebration button, not a form confirmation.
- If user taps "Fix something": input appears with placeholder "What should I change?"

**THE EUFORIA MOMENT — fires when user taps "✓ This is great":**
- Full screen flash: Warm Sand `#e9c46a` overlay, 200ms, fades out
- Large emoji + text animates in: "✦ There it is."
- Below: Chispa's win confirmation message (from Stage 3 prompt)
- Auto-transitions to Screen 5 after 2.5 seconds

**Do not skip the euforia moment. This is the product.**

---

## SCREEN 5 — THE PILL
**Emotional job:** Create the "aha" — they understand what just happened and why it works.

**What the user sees:**
- Full-screen card, centered, generous padding
- Top: small Warm Sand label "💡 What just happened:" (`#e9c46a`)
- Pill text displayed in three visual blocks:
  1. **The concept** — larger font, Burnt Orange `#e76f51`
  2. **The analogy** — normal font, italic
  3. **The question** — normal font, light color, ends with "?"
- Below: single CTA "What's next for me →" (Burnt Orange `#e76f51`)

**Design rules:**
- No chat interface on this screen. This is a moment of reflection, not conversation.
- Warm Sand label (`#e9c46a`) signals "knowledge incoming" — distinct from primary orange.
- The three blocks have visible spacing between them. They breathe.
- The question at the end must visually invite thought — slightly smaller, softer color.
- Pulse animation on card entry (see Design System).

---

## SCREEN 6 — THE MAP
**Emotional job:** Leave them with direction. They know exactly what to do next. No overwhelm.

**What the user sees:**
- Header: "Your next 3 steps" (Syne, white)
- Subtext: "This week. Your job. No jargon." (secondary color, small)
- 3 step cards, numbered, stacked:
  - Number (Burnt Orange `#e76f51`, large)
  - Step text (one sentence, white)
  - Optional: one tool/link if mentioned
- Bottom: two options
  - "Save my map" (Burnt Orange — triggers text copy or share sheet)
  - "Start over" (ghost button — resets session)

**Design rules:**
- Steps are numbered 01 / 02 / 03 — not bullets, not checkboxes.
- No checkboxes. They are not a to-do list. They are a path.
- The "Save my map" action must work without an account. Copy to clipboard minimum.
- No sign-up prompt at the end. This is not a growth hack. This is the finish line.

**Final microcopy (below the map):**
> "One spark. That's how it starts."
> *— Chispa*

---

## MOBILE-FIRST CONSIDERATIONS

- Minimum tap target: 48px height on all interactive elements
- Input bar: fixed to bottom, rises with keyboard (handle viewport resize)
- All text readable at 375px width minimum
- Output card: max 85% screen width, scrollable if long
- Loading states: never leave the screen blank — always show pulsing dots
- Works entirely in browser — no app install, no download, no account required
- Data privacy note (for technical write-up): Gemma 4 architecture supports local deployment in v2 — no user data sent to third parties

---

## WHAT THIS IS NOT

- Not a chat app with a history sidebar
- Not a settings page
- Not a user profile
- Not a dashboard
- Not multi-session (yet)

One flow. Six screens. One win. That's the whole product for v1.

---

*Document created: April 30, 2026*
*Author: Khalena Nasser*
