# NeMo 0.20.0 + Python 3.13.7 Compatibility Research

**Date:** February 24, 2026  
**Issue:** Gemini API calls timeout when called through NeMo  
**Root Cause Under Investigation:** Package version compatibility

---

## Current Environment

**Python:** 3.13.7  
**NeMo Guardrails:** 0.20.0

---

## NeMo 0.20.0 Dependencies

NeMo 0.20.0 requires:
- aiohttp
- annoy
- fastapi
- fastembed
- httpx
- jinja2
- **langchain** ← Critical
- **langchain-community** ← Critical
- **langchain-core** ← Critical
- lark
- nest-asyncio
- pandas
- prompt-toolkit
- protobuf
- pydantic
- pyyaml
- rich
- simpleeval
- starlette
- typer
- uvicorn
- watchdog

---

## Current Installed Versions

| Package | Current Version | Notes |
|---------|-----------------|-------|
| langchain | 1.2.10 (from Feb 2024) | OLD - might be incompatible |
| langchain-core | 1.2.13 | OLD - might be incompatible |
| langchain-google-genai | 4.2.1 | Recent |
| nemoguardrails | 0.20.0 | Current |
| Python | 3.13.7 | Very recent |

---

## Warning Signs (Observed)

1. **stream_usage parameter error:** NeMo passing `stream_usage` to ChatGoogleGenerativeAI which doesn't accept it
2. **Hangs on generate_async():** Works up to LLM init, then hangs indefinitely
3. **No error thrown:** Process just stops, suggests internal deadlock or infinite loop

---

## Hypothesis

**NeMo 0.20.0 was built for Python 3.10/3.11 with older langchain versions**

- Python 3.13.7 introduced changes that may affect async behavior
- langchain 1.2.10 (Feb 2024) might be too old OR too new for NeMo 0.20.0
- Mismatch between what NeMo expects and what langchain provides

---

## What NOT to Do (User's Caution)

❌ Don't blindly upgrade Python (we already fixed Python 3.13.7 conflicts before)  
❌ Don't immediately downgrade packages without checking compatibility  
❌ Don't assume latest versions are best (they break NeMo 0.20.0)

---

## What TO Do Next

### Option 1: Research NeMo 0.20.0 Released Deps (RECOMMENDED)

Find what versions were tested with NeMo 0.20.0:
- GitHub release notes
- NeMo documentation
- requirements.txt in source repo

### Option 2: Try NeMo 0.21.0 or Newer

Might have Python 3.13 fixes and updated deps

### Option 3: Use Mock LLM for Testing

Skip real Gemini for now, test flows with mock responses
- Lets us finish Phase 3 implementation
- Debug NeMo separately

### Option 4: Check NeMo Issue Tracker

Someone else might have reported Python 3.13.7 + Gemini timeout issue

---

## Recommendation

**Before changing ANY packages:**

1. ✅ Research NeMo's official supported versions
2. ✅ Check GitHub issues for "timeout" + "generate_async"
3. ✅ Look at NeMo 0.20.0 requirements.txt
4. ⚠️ ONLY THEN make version changes

**Until research is done:**
- Keep current Python 3.13.7 (user says it works)
- Keep current NeMo 0.20.0
- Don't upgrade packages without understanding dependencies
- Consider mock LLM for workflow continuity

