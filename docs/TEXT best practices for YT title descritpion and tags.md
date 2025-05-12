I am researching best practices for writing a Youtube Video Description, Title and Tags

The ones I have found, I realized that they have many that are subjective, but some are more objective.

**Important Context** : I am building tools that helps creators to optimize their channel by recommending changes. I am explicitly excluding the aspects ofcontent production. My focus is on all the metadata and technical aspects, that are somewhat similar to classical SEO practices but focused in Youtube.

**Limitations** : Consider that I start using only YT Public Data api, with limited information about channels and videos.

**Custom Classification : Objective x Subjective** :
To help with the classification of the best practices, in this context of:
- programming, logically objective, measurable
- with available public data point of view
- whith existing objective data that is not public
- subjective, nuanced and not measurable or logically clear for a code (Python)

Some more information :
- Objective:  use cases that can be described, measured and developed logically
- Subjective :  nuanced and not logically perfect for a python code. Here, maybe LLMs could be a better solution, or fine tude models, all of which are out of scope at this moment,

Final Comment : I am aware that some best practices would not be possible with limited data. Other metadata that I would not have access, but could eventually be objective. And some would depend on the content itself, the script, audience, strategy that are less objective and not public.


**Approach** :
Organize the best practices in three sections according to the context, limitations and classification :

Section 1 : Objective with public data
Section 2 : Objective possible with non public data
Section 3 : Subjective best practices


**TASK** : Considering this context and explanation, I want you to research, summarize, review and refine the best practices for writing Youtube Videos: Title, Description and tags. Then list them based on the
classification and sections.

**Simple and Limited Examples** (comments in parentesis) :

# Section 1 Examples : Objective with public data
- Aim for a description of at least 200-250 words ( calculate the len() of description and compare, setting a upper limit and a scoring method ).
- Formatting Options: Utilize YouTube's formatting options (bold, italics, strikethrough) where appropriate to highlight key information. ( presence of elements Y/N, count of formatting elements x len(), with also a scoring )
- Include Calls to Action (CTAs) and Links ( True/False + counts, etc )

# Section 2 Examples : Objective possible with non public data

- Video File Name: Before uploading, name your video file with relevant keywords (e.g., "how-to-bake-chocolate-chip-cookies.mp4" ( filename is not always acessible publicly , could ask to score )
- initial 100-160 characters (roughly the first 2-3 lines) are critical ( how to measure criticality? )

# Section 3 Examples : Subjective best practices

- Include your main keyword(s) in the first 25-30 words or the first few sentences. ( how to determine the main keywords from only the Title + description + tags, it could be limited or biased )
- Repeat your target keyword 2-4 times naturally throughout the description. ( how to count keywords and rank them without miscounting text ? and how to measure naturalness? or which keywords are the main keywords?  )


**OUTPUT FORMAT:**

Build a new markdown report  with the sections above, listing the best practices in each section, with more details, examples and any other relevant information. The goal is to have up to the Top 7 best practices for each section. Total max is 21 best practices. But it is not mandatory to have 7 best practices for each section, you should aim for relevance and quality over quantity.

1 - list all of the best practices that could work objectively using public available data , suggesting a name per each category and optionally include any known scoring ( ex: max # of chars, max # of words, etc )

2 - list all of the "almost" objective that could be done with more existing data  (not public) ( ex: the filename, or list of the main keywords for that video)

3 - list all the other best practices that are Subjective according to the context and limitations

