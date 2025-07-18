# Autonomous Video Generation Platform – Product Requirements Document (LLM-Optimized)

## 🗂️ Document Purpose and Scope
This markdown PRD is **explicitly structured for consumption by Large Language Models (LLMs)**.  Every section is self-contained and written in declarative, machine-readable style to preserve full context when chunks are provided to an LLM.  The document also embeds **MongoDB schemas and status conventions** so that an LLM‐powered agent can reason about pipeline state, recover from errors, and generate follow-up actions.

---

## 1  Executive Summary
The Autonomous Video Generation Platform converts breaking news (India-focused) into 30-second, 9∶16 vertical videos suitable for YouTube Shorts and Instagram Reels.  Six time-triggered schedulers (running every 6 hours) fetch news, evaluate relevance, generate scripts, create images, produce voice-over videos, and publish to social media.  All metadata is stored in MongoDB.  **Error states are explicitly captured and surfaced to enable autonomous recovery or human intervention**.

---

## 2  System Goals & Success Metrics
| Goal | KPI | Target |
|------|-----|--------|
| Timely content | End-to-end latency | ≤ 6 h from fetch → publish |
| Quality | Engagement rate | ≥ 85 % avg. view completion |
| Reliability | Pipeline success | ≥ 99 % docs reach `POSTED` without error |
| Scalability | Concurrent docs | ≥ 1 000 active per day |

---

## 3  High-Level Architecture
1. **Scheduler 1 – News Fetch**  ➜ `FETCHED / ERROR_FETCH`
2. **Scheduler 2 – Relevance & Sentiment**  ➜ `VALID_ARTICLE / INVALID_ARTICLE / ERROR_VALIDATE`
3. **Scheduler 3 – Script Gen**  ➜ `SCRIPT_GENERATED / ERROR_SCRIPT`
4. **Scheduler 4 – Image Gen**  ➜ `IMAGES_CREATED / ERROR_IMAGES`
5. **Scheduler 5 – Video Gen**  ➜ `VIDEO_GENERATED / ERROR_VIDEO`
6. **Scheduler 6 – Publishing**  ➜ `POSTED / ERROR_POST`

_All schedulers emit structured error details to the same MongoDB document so downstream agents (human or LLM) can diagnose and retry._

---

## 4  Unified MongoDB Document Schema
```jsonc
{
  "_id": "ObjectId",                 // Mongo default
  "headline": "string",             // Original news title
  "article": "string",              // Full article text
  "domain": "Entertainment|Sports|Technology|GeoPolitics|Internal",
  "source": "string",               // Publisher name
  "published_at": "ISO8601",
  /* Pipeline Meta */
  "status": "string",               // Current stage or error status (see enums)
  "relevancy": 0,                    // 0-10, populated in Scheduler 2
  "sentiment": "positive|neutral|negative",
  "video_title": "string",          // Scheduler 2
  "hashtags": ["#tag1", "#tag2"],   // Scheduler 2
  "caption": "string",              // Scheduler 2
  "script": [
      {
        "slide": 1,
        "text": "string",
        "image_query": "string",
        "start_ms": 0,
        "end_ms": 4000
      }
  ],                                   // Scheduler 3
  "image_urls": ["https://..."],    // Scheduler 4
  "voiceover_url": "https://...",   // Scheduler 5
  "video_url": "https://...",       // Scheduler 5
  "youtube_id": "string",          // Scheduler 6
  "instagram_id": "string",        // Scheduler 6
  /* Error Handling */
  "error_type": "string",           // e.g., VALIDATION_API_TIMEOUT
  "error_message": "string",        // Full stack / diagnostic
  "error_at": "ISO8601"             // Timestamp of last failure
}
```

### 4.1  `status` Enum
| Stage | Success | Error |
|-------|---------|-------|
| News fetch | `FETCHED` | `ERROR_FETCH` |
| Relevance check | `VALID_ARTICLE` / `INVALID_ARTICLE` | `ERROR_VALIDATE` |
| Script gen | `SCRIPT_GENERATED` | `ERROR_SCRIPT` |
| Image gen | `IMAGES_CREATED` | `ERROR_IMAGES` |
| Video gen | `VIDEO_GENERATED` | `ERROR_VIDEO` |
| Publish | `POSTED` | `ERROR_POST` |

### 4.2  Error Object Contract
Every scheduler **must** set:
```jsonc
{
  "status": "ERROR_*",            // One of the error enums
  "error_type": "UPSTREAM_502",  // Machine-readable category
  "error_message": "Gemini API returned 502 Bad Gateway after 3 retries.",
  "error_at": "2025-07-18T17:25:00Z"
}
```
Schedulers must leave previous successful fields intact so that partial progress is not lost.

---

## 5  Scheduler Specifications & Update Logic
### 5.1  Scheduler 1 – News Fetch
```
Cron: */360 * * * *
```
1. Query Google News API with filters: country=IN, last 6 h, domains list.
2. **Insert** new doc with `status="FETCHED"`.
3. On failure set `status="ERROR_FETCH"` and populate error fields.

### 5.2  Scheduler 2 – Relevance & Sentiment
Input filter: `{ status: "FETCHED" }`
1. Send article to Gemini.
2. If `relevancy >= 6` ➜ `status="VALID_ARTICLE"`, else `INVALID_ARTICLE`.
3. Capture `sentiment`, `video_title`, `hashtags`, `caption`.
4. Errors ➜ `ERROR_VALIDATE`.

### 5.3  Scheduler 3 – Script Generation
Input: `{ status: "VALID_ARTICLE" }` sorted by `relevancy` desc.
1. Gemini returns slide array (text + image_query + timing).
2. Update document, set `script` array and `status="SCRIPT_GENERATED"`.
3. Errors ➜ `ERROR_SCRIPT`.

### 5.4  Scheduler 4 – Image Generation
Input: `{ status: "SCRIPT_GENERATED" }`
1. Loop slides, call Gemini image endpoint.
2. Upload to GCS bucket `/{YYYY-MM-DD}/{video_title}/images/`.
3. Push `image_urls`, set `status="IMAGES_CREATED"`.
4. Errors ➜ `ERROR_IMAGES`.

### 5.5  Scheduler 5 – Video Generation
Input: `{ status: "IMAGES_CREATED" }`
1. Gemini TTS → `voiceover_url`.
2. FFmpeg composes video with timings, BGM.
3. Upload to GCS `/{YYYY-MM-DD}/{video_title}/video/`.
4. Update `video_url`, `status="VIDEO_GENERATED"`.
5. Errors ➜ `ERROR_VIDEO`.

### 5.6  Scheduler 6 – Publishing
Input: `{ status: "VIDEO_GENERATED" }`
1. Upload to YouTube Shorts & Instagram Reels.
2. Store `youtube_id`, `instagram_id`, set `status="POSTED"`.
3. Errors ➜ `ERROR_POST`.

---

## 6  Global Retry & Alert Strategy
| Severity | Condition | Action |
|----------|-----------|--------|
| Low | First occurrence of any `ERROR_*` | Automatic exponential backoff (max 3) |
| Medium | Same error >3 times in 24 h | Slack alert to #ops-content |
| High | `ERROR_VIDEO` or `ERROR_POST` persists >6 h | PagerDuty escalation |

---

## 7  LLM Context Usage Guidelines
1. **Chunking**: Break this PRD by section headings (`##`) when feeding into an LLM to maintain token efficiency.
2. **Schema Awareness**: Always pass the **Unified MongoDB Schema** chunk alongside task prompts so the LLM can write valid queries/updates.
3. **Status Automata**: Reinforce that `status` follows a strict DFA (finite-state machine) with allowed forward transitions; LLMs must not regress status.
4. **Error Recovery**: Provide the LLM with `error_type` and `error_message` so it can reason about appropriate remedial steps (e.g., retry, skip, manual review).
5. **Few-Shot**: Include example documents for success and failure cases in the prompt when requesting code generation or analysis.

---

## 8  Appendix – Example Documents
### 8.1  Happy Path (Truncated)
```jsonc
{
  "headline": "India clinches test series 2-1",
  "domain": "Sports",
  "status": "POSTED",
  "relevancy": 8,
  "sentiment": "positive",
  "video_title": "Historic Win for Team India!",
  "script": [...],
  "image_urls": [...],
  "video_url": "https://storage/.../video.mp4",
  "youtube_id": "abc123",
  "instagram_id": "179834..."
}
```

### 8.2  Failure Case After Script Generation
```jsonc
{
  "headline": "Market crash fears rise",
  "domain": "Technology",
  "status": "ERROR_IMAGES",
  "relevancy": 7,
  "script": [...],
  "error_type": "GEMINI_IMAGE_RATE_LIMIT",
  "error_message": "429 Too Many Requests for prompt 3 of 6",
  "error_at": "2025-07-18T12:04:09Z"
}
```

---

## 9  Change Log
| Date | Version | Author | Change |
|------|---------|--------|--------|
| 2025-07-18 | 1.0 | LLM-Agent | Initial LLM-optimized PRD with error-aware schema | 