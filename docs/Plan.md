Plan updated


Done:
- ~~Move new Dataload to Utils~~
- ~~Add Channel and clean parquet files~~
- ~~make Channel View for better channels df~~

Pending:
- Filter Class + wrapper + ui for multi DFs
- DebugTools inspect Nan, Null, 0, etc
- Decide on datacleaning to be integrated on Dataload ?
- clean Analytics2 ( bare minimum)
- Metadata inspector on best practices
- Custom Filter Logic: Allow for custom filter logic (e.g., ranges, regex) if your analysis requires it.


```code :
# Summary Table (Markdown)
| Component | Method/Usage | Input | Output | Notes |
|-----------------------|-------------------------------|-------------------------|-----------------------|----------------------------------------------------------|
| FilterManager | render_filters(dataframe) | DataFrame | Updates session state | Renders UI for filters, stores user selections |
| FilterManager | get_filter_state() | None | Dict | Returns current filter selections from session state |
| FilterManager | apply_filters(df) | DataFrame | Filtered DataFrame | Applies selected filters to a DataFrame |
| FilterManager | render_filter_summary() | None | UI summary | Shows a compact summary of active filters |
| Main Page (host) | Renders popover + summary | N/A | N/A | Should host the filter UI and summary for all subpages |
| Subpage/Section | Receives filtered df(s) | Filtered DataFrame(s) | Plots, tables, etc. | Should only use filtered dfs provided by main page |
| Helper Function (TBD) | To enforce local filtering | df, filter_manager | Filtered DataFrame | Ensures all filtering happens on local copy |
```


"[YouTube Metadata Best-Practice Checklist.md](/app/docs/YouTube%20Metadata%20Best%E2%80%91Practice%20Checklist.md)"
"[test](/docs/YouTube%20Metadata%20Best-Practice%20Checklist.md)"

content = """# YouTube Metadata Best‑Practice Checklist
*(Implementation‑ready metrics & future roadmap)*

## 1  Implementation‑Ready Checklist
These items can be scored automatically with **only the public fields returned by the YouTube Data API v3** (e.g. `snippet.*`, `contentDetails.*`).

| # | Best Practice | Public API Fields | Goal / Threshold | Simple Scoring Formula | Channel‑Relative Bonus* |
|---|---------------|------------------|------------------|------------------------|-------------------------|
| 1 | **Concise Title** – keep ≤ 60 characters | `snippet.title` | 20–60 chars | `score = 1 if len(title) <= 60 else 0` | Compare to channel median title length; flag if > +1 SD above median |
| 2 | **Keyword Early** – main keyword appears in first 30 chars of title | `snippet.title` | kw pos \< 30 | `score = 1 if pos < 30 else 0` | Use most‑common unigram across channel titles as “main keyword” baseline |
| 3 | **Rich Description Length** – between 200 words and 5 000 chars | `snippet.description` | 200–5 000 chars | `score = min( len_chars / 5000 , 1 )` | Channel “normal” = median description length; show % difference |
| 4 | **Chapters/Timestamps Present** – ≥ 3 timestamps starting at `0:00` | `snippet.description` | Regex `^0:00` + ≥ 3 matches | `score = min( count/3 , 1 )` | Report avg chapters per video in channel |
| 5 | **Hashtags Within Limit** – ≤ 60 hashtags & placed at end | `snippet.description` | count ≤ 60 | `score = 1 if count<=60 else 0` | Median hashtags per video across channel |
| 6 | **Basic Formatting Used** – bold / italic / strikethrough / lists | `snippet.description` | ≥ 1 formatting token | `score = min(tokens/5, 1)` | Show ratio tokens ∕ chars vs channel average |
| 7 | **Clear CTA & Link** – at least one CTA phrase **and** URL | `snippet.description` | CTA regex & URL present | `score = 1 if both True else 0` | Compare CTA frequency to channel mean |

\*Bonus calculation example (Description Length)

```text
best practice range: 200–5 000 chars
channel range (P10–P90): 300–1 200 chars
current video: 1 700 chars (≈ 42 % above channel P90; consider shortening)






Ignored:
/app/z_Do_Not_Sync_or_use
/app/!1 TO CLEAN




1 - Here’s a summary of the necessary changes for moving /app/data/dataloader.py (and its key functions) to /app/utils, and updating all affected files in /app/modules:

Main file: /app/data/dataloader.py → /app/utils/dataloader.py
All internal imports that use from utils.config import APPMODE will still work, since the file will be in /app/utils.
Any references to data/ (such as "data/tbl_nerdalytics.parquet") in the code will need to be updated to reflect the new relative path, since the working directory for relative paths may change when the file is imported from a different location. If the current working directory is always /app, then "data/..." will still work. If the code uses file or os.path for relative paths, these may need to be updated to use the correct base directory.
The functions load_data, load_base_data, get_user_dataframe, and deduplicate_playlist_data will be moved as-is, but any references to file paths or directories should be checked to ensure they still work correctly.
All files in /app/modules that import or use dataloader, load_data, load_base_data, or get_user_dataframe:
These files import from data.dataloader and will need to update to from utils.dataloader import ... (or similar):

/app/modules/analytics2.py
from data.dataloader import load_data → from utils.dataloader import load_data
/app/modules/debugtools.py
from data.dataloader import load_data → from utils.dataloader import load_data
/app/modules/blocks/debugtools1.py
from data.dataloader import load_data → from utils.dataloader import load_data
/app/modules/blocks/template_playlist_block.py
from data.dataloader import get_user_dataframe → from utils.dataloader import get_user_dataframe
/app/modules/blocks/template_nerdalytics_block.py
from data.dataloader import get_user_dataframe → from utils.dataloader import get_user_dataframe
/app/modules/blocks/template_slope_block.py
from data.dataloader import get_user_dataframe → from utils.dataloader import get_user_dataframe
/app/modules/templatedatapage.py
from data.dataloader import get_user_dataframe → from utils.dataloader import get_user_dataframe
Summary of changes:
Main file (/app/data/dataloader.py → /app/utils/dataloader.py):

Move the file to /app/utils/dataloader.py.
Check and update any relative path references for parquet files if needed (e.g., "data/tbl_nerdalytics.parquet"). If the working directory is always /app, these paths will still work, but if not, consider using absolute paths or os.path.join with a known base directory.
All internal imports (e.g., from utils.config import APPMODE) will continue to work.
Other files in /app/modules:

Update all imports from data.dataloader to utils.dataloader.
No other code changes are needed unless there are hardcoded paths assuming the dataloader is in /app/data (none found in the search results).
Follow-up questions for you before proceeding:

Is the working directory always /app when running your Streamlit app? If so, the relative "data/..." paths will still work after moving the file. If not, should I update the dataloader to use absolute paths (e.g., with os.path.join and a base directory)?
Do you want to move all of dataloader.py, or only the functions load_data and load_base_data? (Your request suggests moving the whole file, but please confirm.)
Is it OK to update all imports in /app/modules as described above?
Once you confirm these points, I’ll proceed with the code changes. Would you like to clarify any of the above before I begin?

Feedback submitted
Generating...


