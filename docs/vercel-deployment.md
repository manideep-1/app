# Vercel deployment (frontend only)

This project deploys **only the frontend** to Vercel. The backend runs elsewhere.

## 1. Project settings (Vercel Dashboard)

In your Vercel project: **Settings → General**:

| Setting | Value |
|--------|--------|
| **Root Directory** | `frontend` |
| **Framework Preset** | Create React App (or leave as Other) |
| **Build Command** | `npm run build` (or `yarn build`) |
| **Output Directory** | `build` |
| **Install Command** | `npm install` (or `yarn`) |

Save after changing **Root Directory** so that builds run from the `frontend` folder.

## 2. Why you were getting 404

- The app is a **single-page app (SPA)**. There is only one real file: `index.html`. All routes (`/dashboard`, `/problems`, `/coach`, `/login`, etc.) are handled by **React Router** in the browser.
- When you **click links** in the app, the browser never requests those paths from the server; React Router just swaps the view → no 404.
- When you **open a URL directly** or **refresh** on e.g. `/dashboard`, the browser asks the **server** for `/dashboard`. Vercel looks for a file at that path, finds nothing (only `index.html` at `/`), and returns **404**.
- **Fix:** `frontend/vercel.json` uses **rewrites** so that every path is served with `/index.html`. The same React app loads every time, and React Router then shows the correct route.

## 3. Files that matter

| File | Purpose |
|------|--------|
| `frontend/vercel.json` | Rewrites all routes to `/index.html` for SPA + React Router. |
| `frontend/package.json` | No change needed. `"build": "craco build"` already produces the `build` folder. |

## 4. SPA rewrites (vercel.json)

`frontend/vercel.json`:

```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

- Every request is rewritten to `/index.html`.
- Static assets (JS, CSS, images) are still served from `build` because Vercel matches actual files first; only non-file paths hit the rewrite.

## 5. React Router

No code changes are required. The app uses `BrowserRouter` and routes at `/`, `/login`, `/dashboard`, `/problems`, `/coach`, etc. With the rewrites above, direct visits and refreshes on those routes now serve `index.html`, and React Router handles the path as usual.
