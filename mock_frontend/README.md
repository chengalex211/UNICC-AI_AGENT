# mock_frontend — static demo UI only

This package is a **non-production** React + Vite + TypeScript UI used for **layout, copy, and flow prototyping**. It does **not** call the evaluation API.

## Behavior

- **NewEvaluation**: submit uses `setTimeout` (~2.2s) then navigates; no `fetch` to `frontend_api`.
- **Dashboard / Report**: data comes from `src/data/mockData.ts`, shaped similarly to a full `CouncilReport` JSON for visual parity only.

## When to use

- Designers or PMs reviewing screens without Python/API setup.
- Comparing Figma or copy against static pages.

## Production app

Use **`../real_frontend/`** with **`../frontend_api/`** on port **8100** — see:

- `docs/system-overview.en.md`
- `docs/system-overview.zh-CN.md`

## Run

```bash
cd mock_frontend
npm install
npm run dev
```

## Location in monorepo

`mock_frontend/` lives at the **Capstone repository root** (sibling to `real_frontend/` and `UNICC-Project-2/`). The old `UNICC-Project-2/frontend/` copy was removed; this folder is the canonical mock UI.
