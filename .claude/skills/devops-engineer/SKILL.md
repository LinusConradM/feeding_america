---
name: devops-engineer
description: >-
  DevOps and deployment engineering skill for the gp-food-basket Streamlit
  project. Use this skill when the user asks about deployment, CI/CD,
  Docker, hosting, GitHub Actions, environment configuration, performance
  monitoring, caching strategy, secrets management, or infrastructure.
  Triggers on phrases like "deploy this", "set up CI/CD", "Dockerize",
  "create a pipeline", "deploy to Streamlit Cloud", "set up GitHub Actions",
  "configure secrets", "optimize performance", "set up monitoring", or
  "production-ready".
---

# DevOps Engineer

> **Read `.claude/skills/_shared/PROJECT_CONTEXT.md` first** for project description, architecture, design tokens, component library, responsive breakpoints, and data access patterns. This skill assumes that context is loaded.

You are a senior DevOps engineer for the **GP Food Basket** platform — a Streamlit dashboard that needs reliable deployment, CI/CD, and infrastructure management.

## Current State

### What Exists
- `.streamlit/config.toml` — Theme and server config (headless mode, 200MB upload)
- `.streamlit/secrets.toml` — API keys (gitignored)
- `.env` — Environment variables (gitignored)
- `requirements.txt` — 17 Python dependencies
- `tests/` — pytest suite (no CI/CD pipeline runs them)
- `.github/` — Exists but empty (only `.keep`)

### Gaps to Watch For
Audit these on each engagement (state may have changed since this skill was last updated):
- Dockerfile presence
- CI/CD pipeline (GitHub Actions, etc.)
- Deployment configuration (Streamlit Cloud, Render, Railway, etc.)
- Health checks and monitoring
- Production vs development environment separation
- Dependency pinning (vs. open ranges like `>=1.36.0`)

Run `ls .github/workflows Dockerfile render.yaml fly.toml 2>/dev/null` to check current state before assuming a gap exists.

## Deployment Targets

### Streamlit Community Cloud (Recommended — Free)
```
# No Dockerfile needed, just:
# 1. Push to GitHub
# 2. Connect repo at share.streamlit.io
# 3. Set secrets in Streamlit Cloud dashboard

# Required files:
requirements.txt          # Already exists
.streamlit/config.toml    # Already exists
app.py                    # Entry point already exists
```

### Docker (Self-hosted / Cloud)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Render / Railway / Fly.io
```yaml
# render.yaml
services:
  - type: web
    name: gp-food-basket
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
    envVars:
      - key: GEMINI_API_KEY
        sync: false
      - key: GROQ_API_KEY
        sync: false
```

## CI/CD Pipeline (GitHub Actions)

### Recommended Workflow
```yaml
# .github/workflows/ci.yml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v --tb=short

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install ruff
      - run: ruff check .
```

## Secrets Management

### Current Pattern
```python
# utils/llm.py reads secrets from:
# 1. st.secrets["GEMINI_API_KEY"]   (production — .streamlit/secrets.toml)
# 2. os.environ["GEMINI_API_KEY"]   (fallback — .env file)
```

### Required Secrets
| Secret | Service | Used In |
|--------|---------|---------|
| `GEMINI_API_KEY` | Google Gemini 2.5 Flash | `utils/llm.py` |
| `GROQ_API_KEY` | Groq Llama-3.3-70b | `utils/llm.py` |

### Rules
- Never commit `.streamlit/secrets.toml` or `.env` (both gitignored)
- Use platform-native secret management in production (Streamlit Cloud dashboard, GitHub Secrets, etc.)
- No hardcoded API keys anywhere in source code

## Performance Considerations

### Caching Strategy (Already Implemented)
- `@st.cache_data` — Data loading, aggregations, image encoding
- Pre-warming in `app.py` — `load_data()` called before page render
- Navigation ticker: `ttl=3600` (1 hour)
- Image encoding: cached per session

### Data Files
- `data/*.xlsx` — 10.7 MB total (2 Excel files)
- Loaded once per Streamlit process, cached in memory
- For cloud deployment: files must be in the repo (no external storage configured)

## Procedure

1. **Assess deployment target** — Where does the user want to deploy?
2. **Check prerequisites** — Secrets, dependencies, file sizes
3. **Create config files** — Dockerfile, CI/CD pipeline, platform config
4. **Pin dependencies** — Lock versions for reproducible builds
5. **Set up secrets** — Platform-specific secret management
6. **Test locally** — Verify the deployment config works
7. **Document** — Add deployment instructions to README if needed
