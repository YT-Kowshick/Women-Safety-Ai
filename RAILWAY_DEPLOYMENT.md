# Railway Deployment Guide (Backend + Frontend)

This project is a monorepo with:
- `backend/` (FastAPI)
- `frontend/` (Vite React)

Deploy as **2 Railway services** from the same GitHub repo.

---

## 1) Push latest code to GitHub

Make sure your repo includes:
- `backend/nixpacks.toml`
- `backend/Procfile`
- `frontend/nixpacks.toml`
- `frontend/package.json` (`start` script)

---

## 2) Create Railway project

1. Open Railway dashboard.
2. Click **New Project** → **Deploy from GitHub repo**.
3. Select this repository.

---

## 3) Deploy Backend service

1. Add a new service from the same repo.
2. Set **Root Directory** to `backend`.
3. Railway will use `backend/nixpacks.toml`.
4. Wait for deploy, then open backend URL:
   - `https://<your-backend>.up.railway.app/health`
   - should return `{ "status": "ok" }`

No extra environment variables are required for backend.
For stricter CORS in production, set:

```env
ALLOWED_ORIGINS=https://<your-frontend>.up.railway.app
```

---

## 4) Deploy Frontend service

1. Add another service from the same repo.
2. Set **Root Directory** to `frontend`.
3. In frontend service Variables, add:

```env
VITE_API_URL=https://<your-backend>.up.railway.app
```

4. Redeploy frontend service after setting variable.

Railway uses `frontend/nixpacks.toml` to build and run.

---

## 5) Verify end-to-end

- Open frontend public URL.
- Check pages that call API (Safety Check, Trends, Leaderboard).
- If API errors appear, ensure `VITE_API_URL` points to backend URL **without trailing slash**.

---

## 6) Optional: custom domains

In each Railway service:
- Settings → Domains → Add custom domain.

---

## Troubleshooting

### Backend starts but endpoints fail
- Confirm model/data files exist in `backend/`:
  - `CrimesOnWomenData.csv`
  - `safety_model.pkl`

### Frontend shows network error
- Verify frontend variable is exactly:
  - `VITE_API_URL=https://<backend-domain>`
- Redeploy frontend after changing environment variables.

### CORS blocked in browser
- Set backend variable:
  - `ALLOWED_ORIGINS=https://<frontend-domain>`
- Redeploy backend service.

### Build fails in frontend
- Ensure lockfile and `package.json` are committed.
- Re-run deploy after clearing failed deployment.
