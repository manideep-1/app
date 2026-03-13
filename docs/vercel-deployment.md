# Vercel deployment (frontend only)

This project deploys **only the frontend** to Vercel. The backend runs elsewhere (e.g. Railway, Render, Fly.io).

## Why login, signup, and other API features don’t work on Vercel

On Vercel the app is **static only**. There is no server handling `/api/*`. The frontend decides where to send API requests:

- **Local dev:** It uses `http://127.0.0.1:8000` (or the proxy).
- **Production:** If `REACT_APP_BACKEND_URL` is **not set**, it uses **same-origin** `/api` (e.g. `https://your-app.vercel.app/api/...`). Vercel only serves your built files, so those requests are not handled by a backend → **login, signup, dashboard, coach, etc. all fail**.

**Fix:** Deploy your backend somewhere and set `REACT_APP_BACKEND_URL` in Vercel to that URL (see below). The backend must also allow your Vercel frontend origin in CORS.

---

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

## 2. Environment variables (required for login/signup)

In Vercel: **Settings → Environment Variables**. Add:

| Name | Value | Required |
|------|--------|----------|
| **REACT_APP_BACKEND_URL** | Your backend base URL, e.g. `https://your-app.railway.app` or `https://api.yourdomain.com`. Do **not** add `/api` — the app appends it. | **Yes** (for login, signup, problems, coach, etc.) |
| **REACT_APP_GOOGLE_CLIENT_ID** | Your Google OAuth client ID (for “Sign in with Google”). | Only if you use Google sign-in |

After adding or changing these, **redeploy** the project (Deployments → … → Redeploy) so the build picks up the new values.

### Backend CORS

Your backend must allow the Vercel frontend origin. Set this on the **backend** (e.g. in its env):

- **CORS_ORIGINS** = your Vercel URL(s), e.g. `https://your-app.vercel.app` or `https://your-app.vercel.app,https://your-app-*.vercel.app` for preview URLs.

Do **not** use `*` if the backend uses credentials (cookies/auth headers); list the exact frontend origin(s).

## 3. Why you were getting 404 (SPA routes)

- The app is a **single-page app (SPA)**. There is only one real file: `index.html`. All routes (`/dashboard`, `/problems`, `/coach`, `/login`, etc.) are handled by **React Router** in the browser.
- When you **click links** in the app, the browser never requests those paths from the server; React Router just swaps the view → no 404.
- When you **open a URL directly** or **refresh** on e.g. `/dashboard`, the browser asks the **server** for `/dashboard`. Vercel looks for a file at that path, finds nothing (only `index.html` at `/`), and returns **404**.
- **Fix:** `frontend/vercel.json` uses **rewrites** so that every path is served with `/index.html`. The same React app loads every time, and React Router then shows the correct route.

## 4. Files that matter

| File | Purpose |
|------|--------|
| `frontend/vercel.json` | Rewrites all routes to `/index.html` for SPA + React Router. |
| `frontend/package.json` | No change needed. `"build": "craco build"` already produces the `build` folder. |

## 5. SPA rewrites (vercel.json)

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

## 6. React Router

No code changes are required. The app uses `BrowserRouter` and routes at `/`, `/login`, `/dashboard`, `/problems`, `/coach`, etc. With the rewrites above, direct visits and refreshes on those routes now serve `index.html`, and React Router handles the path as usual.
