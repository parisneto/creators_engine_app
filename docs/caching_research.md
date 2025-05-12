https://chatgpt.com/c/681e63bf-8cbc-8010-8d12-25ed906f4341


**Clarifying caching and plotting**

I’ll respond to the user’s questions based on previous explanations but go deeper into specific points. Browsing isn’t needed because the info on Streamlit and caching is stable and doesn’t require current event updates. When it comes to the caching rules and dataframes, I’ll provide a rule template in triple quotes. I need to clarify st.cache\_data.clear vs .clear and explain that st.cache\_data is a decorator, and calling .clear clears an instance. I’ll also suggest methods for on-demand plot loading, using tabs or session state flags.


Thought for 9 seconds


Below I answer each question, tighten a couple of earlier details, and then give you the **LLM-assist rule block** you asked for.

---

## 1. Which decorator where?

| Layer                                                  | What lives here                             | Decorator                                                               | Why                                                                             |
| ------------------------------------------------------ | ------------------------------------------- | ----------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| **Core dataframes**<br>(full tables read from Parquet) | *Same for every user all day*               | `@st.cache_resource(ttl="1d")`                                          | One copy per Cloud-Run instance, negligible RAM growth, no Arrow serialization. |
| **Per-user filtered / mutated views**                  | *Depends on widgets in that user’s session* | `@st.cache_data(ttl="10m")` **or** just keep them in `st.session_state` | Each user gets an independent object they can mutate safely.                    |

So yes—core DFs → `cache_resource`; user-specific sub-sets → `cache_data` (or session state if you don’t need cross-rerun caching).

---

## 2. Metaphor check

*Almost*:

* **“Shallow copy”** ≈ the exact object held by `cache_resource`.
* **“Deep copy”** ≈ the serialized/deserialized instances returned by `cache_data`.

Just remember that with `cache_data` you *could* also mutate the copy you get; with `cache_resource` you should `.copy()` first if you plan to mutate.

---

## 3. Pre-processing vs. local tweaks

| Step                                                                 | Where to run                                                           | Store result in                                             |
| -------------------------------------------------------------------- | ---------------------------------------------------------------------- | ----------------------------------------------------------- |
| Type coercion, column adds, joins that *never* change during the day | Inside the `@st.cache_resource` loader right after `pd.read_parquet()` | Return the ready-to-use clean DFs.                          |
| Widget-driven filtering, dropping NA for a specific plot, etc.       | In each page **after** you call `load_daily_data()`                    | Either `st.cache_data` (if heavy) or plain code (if light). |

---

## 4. About Plotly’s full bundle & “on-demand” plots

* **Config flag:**

  ```python
  st.plotly_chart(
      fig,
      use_container_width=True,
      config={"staticPlot": True}   # <- makes it behave like a PNG
  )
  ```

  *`staticPlot: True`* removes the JS bundle and interactivity; good for large scatter charts where hover & zoom are not essential.

* **Render-on-demand pattern**

  ```python
  tab1, tab2 = st.tabs(["📊 Overview", "📈 Heavy Plot"])
  with tab2:
      if st.button("Generate plot"):
          fig = make_big_plot(...)
          st.plotly_chart(fig)
  ```

  or wrap in `st.expander`.  That way the expensive figure is only built when a user explicitly asks.

---

## 5. `.clear()` and manual GC

* **`load_daily_data.clear()`**
  Every function wrapped by a Streamlit cache decorator gains a `.clear()` method. Calling it invalidates its stored value immediately—handy if you push new Parquet files and want the container to reload them without waiting for tomorrow.

* **Manual `gc.collect()` button**
  Purely a debugging aid. If you suspect a leak, insert it, click it a few times while watching Cloud-Run memory graphs. Once you’re happy, remove it.

You do **not** need either of these in every page header; treat them as admin tools.

---

## 6. Project-specific caching rule block for the LLM assistant

```yaml
# Project Principles – DataFrames & Caching

caching:
  core_loader:
    decorator: "@st.cache_resource(ttl='1d')"
    rules:
      - Load parquet files once per container start.
      - Perform all permanent preprocessing inside the loader
        (type fixes, joins, computed columns).
      - Return a dict of clean DataFrames; DO NOT mutate later.
  user_views:
    decorator: "@st.cache_data(ttl='10m')"   # adjust TTL as needed
    rules:
      - Use for expensive per-user derivations (group-bys, stats).
      - Always call .copy() before mutating.
      - Alternatively store small filters directly in st.session_state.
  invalidation:
    rules:
      - Call <loader>.clear() after writing fresh parquet files.
      - Container restart also refreshes everything.

plotting:
  plotly:
    rules:
      - For heavy charts, wrap creation in a button/tab/expander so
        it only runs on demand.
      - When interactivity is not required, render with
        st.plotly_chart(fig, config={"staticPlot": True}).

memory_debugging:
  rules:
      - Temporary: add a "Force GC" st.button calling gc.collect()
        while profiling leaks; remove in production.
```

---

### Anything still unclear?

If you need examples of `.clear()` orchestration, or want to sanity-check memory footprint estimates, let me know!
