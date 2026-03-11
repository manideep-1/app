# If Else – Theming & Color System

All UI colors are controlled from **one place**: `frontend/src/index.css` (CSS custom properties under `:root`). Tailwind uses these via `tailwind.config.js`. Do not introduce new colors in components; use or extend these tokens.

## Rules

- **No pink** anywhere: backgrounds, buttons, hover, focus, borders, gradients, badges, animations.
- Use **theme tokens only**; avoid hardcoded hex/rgba in components (except where a token is not available and you add one in `index.css` first).

## Token Map

| Token         | Purpose              | Intent        |
|---------------|----------------------|---------------|
| `--primary`   | Main actions, links  | Blue (#2563eb) |
| `--secondary`| Secondary buttons, subtle UI | Neutral slate (gray) |
| `--accent`   | Hover/alternate emphasis | Teal |
| `--destructive` | Errors, delete actions | Red |
| `--success`  | Success states       | Green |
| `--warning`  | Warnings             | Amber |
| `--muted`    | Subtle backgrounds  | Gray |
| `--border`, `--input`, `--ring` | Borders, inputs, focus ring | Neutral / primary |

## Where to change colors

- **Global theme:** `frontend/src/index.css` → `:root { --primary: ...; }`
- **Tailwind:** `frontend/tailwind.config.js` only references `hsl(var(--...))`; add new tokens in `index.css` and in `theme.extend.colors` if needed.

## Glow / shadows

The `glow` animation and any button shadow use **primary blue** (`rgba(37, 99, 235, ...)`). Do not use pink in keyframes or shadow utilities.
