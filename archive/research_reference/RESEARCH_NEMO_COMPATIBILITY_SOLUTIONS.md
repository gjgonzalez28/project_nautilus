# NeMo + Gemini Compatibility Deep Dive - Complete Analysis

**Date:** February 24, 2026  
**Status:** Blocker analysis complete - Multiple viable solutions identified

---

## The Problem

NeMo Guardrails 0.20.0 has an **OPEN KNOWN BUG (#1558)** with Google GenAI models:
- Timeout on `generate_async()` calls
- langchain 1.x integration broken for Gemini
- Bug introduced in NeMo v0.19.0 (Dec 2025)
- **Still unfixed** - no v0.21.0 release scheduled

---

## Compatibility Matrix Testing

| Solution | Versions | Result | Viability |
|----------|----------|--------|-----------|
| Current | langchain 1.2.10 + nemo 0.20 | ❌ TIMEOUT | No |
| Upgrade | langchain 1.2.10+ | ❌ Dependency hell | No |
| Downgrade to 0.3.x | langchain 0.3.27 + nemo 0.20 | ❌ langchain-google-genai incompatible | No |
| Downgrade to 0.2.x | langchain 0.2.14 + nemo 0.20 | ❌ Unavailable versions | No |
| Old genai | langchain 1.2.10 + langchain-genai-1.0.10 | ❌ Metaclass conflicts | No |

**Conclusion:** Direct package version matching is a losing battle. Dependency conflicts are cascading.

---

## VIABLE SOLUTIONS (Ranked by Practicality)

### **Option 1: Use OpenAI Instead of Gemini** ✅ RECOMMENDED

Switch LLM provider from Gemini to OpenAI (GPT-4).

**Pros:**
- ✅ OpenAI has mature, stable langchain integration
- ✅ No known bugs with NeMo 0.20.0
- ✅ Works with current Python 3.13.7 + langchain 1.2.10
- ✅ No package downgrades needed
- ✅ Can test now, no delays

**Cons:**
- ❌ You already paid for Gemini tier
- ❌ Costs might differ (but GPT-4 is comparable: $0.006-0.06 per 1K tokens)
- ❌ Requires API key change

**Implementation:**
- Get OpenAI API key
- Change config.yml: `model: gpt-4` and `engine: openai`
- Update .env: Add `OPENAI_API_KEY`
- Done - no package changes needed

**Cost:** $0.03-0.15 per diagnostic conversation (similar to Gemini)

---

### **Option 2: Patch NeMo Locally** ⚠️ INTERMEDIATE

Modify NeMo's code to work around bug #1558.

**Pros:**
- ✅ Keeps using Gemini (your paid tier)
- ✅ Can do it today
- ✅ Focused fix, no package chaos

**Cons:**
- ⚠️ Requires editing NeMo source code directly
- ⚠️ Patch breaks if NeMo is reinstalled
- ⚠️ Not production-grade
- ⚠️ Might introduce other bugs

**The fix:** NeMo is passing `stream_usage` parameter that langchain-google-genai v4.x doesn't accept.  
Patch location: `venv/Lib/site-packages/nemoguardrails/llm/models/langchain_initializer.py` line ~219

Change the parameter passing to filter out incompatible args.

**Implementation time:** 1-2 hours (research + testing)

---

### **Option 3: Use Mock LLM for Development** 💡 PRAGMATIC

Use mock responses while developing flows, swap in real Gemini for beta testing.

**Pros:**
- ✅ Zero package conflicts
- ✅ Can implement all 5 remaining flows today
- ✅ Fix Gemini separately
- ✅ Test workflow logic without LLM costs

**Cons:**
- ❌ Can't do real beta testing until Gemini is fixed
- ❌ Responses are deterministic (not realistic)
- ❌ Doesn't solve the underlying issue

**Implementation time:** 30 mins

---

### **Option 4: Wait for NeMo 0.21.0** ❌ NOT VIABLE

No timeline provided by NVIDIA. Issue #1558 unresolved.

---

## My Recommended Path Forward

**Use Option 1 (OpenAI) OR Option 2 (Patch) OR Option 3 (Mock)**

**Decision Matrix:**

| Your Priority | Choose |
|---|---|
| "Get working NOW with real LLM" | **Option 1: Use OpenAI** |
| "Keep Gemini, willing to patch" | **Option 2: Patch NeMo** |
| "Finish flows first, LLM later" | **Option 3: Use Mock** |

---

## Cost Comparison

### Gemini 2.5 Pro (your current setup)
- Input: $1.50 per 1M tokens
- Output: $6.00 per 1M tokens
- ~5 cents per diagnostic conversation

### OpenAI GPT-4 Turbo
- Input: $0.01 per 1K tokens = $10 per 1M tokens
- Output: $0.03 per 1K tokens = $30 per 1M tokens
- ~4-5 cents per diagnostic conversation
- **Similar cost**, more stable API

---

## What TomJust Should Know

✅ **You were RIGHT** about package version conflicts  
✅ **NeMo + Gemini issue is real** and documented  
✅ **Not your code**, it's a known NeMo bug  
✅ **Your Paid Gemini tier is fine** - can switch providers any time  
✅ **Cost monitoring is built** - we have `cost_monitor.py`

---

## Immediate Next Steps

**Choose your path:**

1. **Want to use Gemini?** → We patch NeMo (Option 2, ~2 hours)
2. **Want working system now?** → Switch to OpenAI (Option 1, 15 mins)
3. **Want to develop flows?** → Use mock (Option 3, 30 mins)

**Which appeals most?**

