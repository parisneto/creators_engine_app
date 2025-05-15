
# YouTube Metadata Best-Practice Checklist
*(Implementation-ready metrics & future roadmap)*

---

## 1  Implementation-Ready Checklist
These items can be **scored automatically** with only the public fields returned by the **YouTube Data API v3** (e.g. `snippet.*`, `contentDetails.*`).

| # | Best Practice | Public API Field(s) | Goal / Threshold | Simple Scoring Formula | Channel-Relative Bonus* |
|---|---------------|---------------------|------------------|------------------------|-------------------------|
| 1 | **Concise Title** – keep ≤ 60 characters | `snippet.title` | 20 – 60 chars | `score = 1 if len(title) <= 60 else 0` | Compare to channel median title length; flag if > +1 SD |
| 2 | **Keyword Early** – main keyword in first 30 chars of title | `snippet.title` | kw pos \< 30 | `score = 1 if pos < 30 else 0` | Use channel-wide most-common unigram as baseline |
| 3 | **Rich Description Length** – 200 words – 5 000 chars | `snippet.description` | 200 – 5 000 chars | `score = min(len_chars/5000, 1)` | % above/below channel median description length |
| 4 | **Chapters Present** – ≥ 3 timestamps starting `0:00` | `snippet.description` | Regex `^0:00` + ≥ 3 | `score = min(count/3, 1)` | Avg chapters per video in channel |
| 5 | **Hashtags ≤ 60 & placed at end** | `snippet.description` | count ≤ 60 | `score = 1 if count <= 60 else 0` | Median hashtags per video |
| 6 | **Basic Formatting Used** – bold / italic / strikethrough / lists | `snippet.description` | ≥ 1 formatting token | `score = min(tokens/5, 1)` | Tokens ∕ chars vs channel average |
| 7 | **Clear CTA + Link** present | `snippet.description` | CTA regex & URL | `score = 1 if both True else 0` | CTA frequency vs channel mean |

\*Example bonus calculation (Description Length):

```text
Best-practice range: 200 – 5 000 chars
Channel P10–P90:      300 – 1 200 chars
Current video:        1 700 chars  (≈ 42 % above P90 → consider shortening)
````

---

## 2  Future Roadmap

### 2.1  Objective Items Requiring Creator-Only Data

| # | Practice                                                        | Extra Data Needed                        |
| - | --------------------------------------------------------------- | ---------------------------------------- |
| 1 | Keyword-rich **video file name** (`matcha-whisking.mp4`)        | `fileName` (owner-only)                  |
| 2 | Optimised **Tags** – first 3 contain keyword, total ≤ 500 chars | `snippet.tags` (write)                   |
| 3 | **Custom Thumbnail** – 1280 × 720 & keyword in file name        | Thumbnail upload meta                    |
| 4 | Accurate **Closed Captions** uploaded / edited                  | `captions` API                           |
| 5 | **End-screens & Cards** linking to playlists / site             | `endScreen`, `cards`                     |
| 6 | Specific **Category**, recording **date/location** set          | `snippet.categoryId`, `recordingDetails` |
| 7 | Correct **defaultLanguage** & **defaultAudioLanguage**          | `snippet` fields                         |

### 2.2  Subjective / Heuristic Items (ideal for LLM or A/B testing)

* Craft an **emotional hook** in the first 25 words of description
* Repeat main keyword **naturally** 2 – 4 × (avoid stuffing)
* Use **numbers / brackets / power-words** in titles (“5 Ways…”, “\[2025]”, etc.)
* Keep **brand voice & tone** consistent across metadata
* Limit **ALL-CAPS & emoji** to emphasise (≤ 1 emoji, minimal caps)
* Align description keywords with *spoken* transcript content
* Lead with **viewer benefits** before self-promo links

---

## 3  References & Further Reading

1. [Search Engine Land – Optimal title length](https://searchengineland.com/title-tag-length-388468)
2. [Backlinko – YouTube SEO Study](https://www.briggsby.com/reverse-engineering-youtube-search) – recommends 200-350 word descriptions
3. [YouTube Help – Video Chapters](https://support.google.com/youtube/answer/9884579)
4. [YouTube Community – 60 Hashtag limit](https://support.google.com/youtube/thread/289715480)
5. [RouteNote – Bold/Italic formatting in descriptions](https://routenote.com/blog/bold-italics-and-strikethrough-text-in-youtube/)
6. [SocialBee – Effective CTAs on YouTube](https://socialbee.com/blog/cta-youtube/)

---

> **Usage**: paste this entire block into your code-assisted IDE or documentation.
> Implement simple Python validators for Section 1 now, and track Section 2/3 items as backlog tasks.

```
```
