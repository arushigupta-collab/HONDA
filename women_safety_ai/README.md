Women Safety Persona Chat
=========================

**Overview**  
This Streamlit prototype explores women’s safety scenarios through synthetic personas. Personas blend demographic context, sentiment cues, and memory to simulate first-person narratives about navigating Indian cities. The app also visualizes illustrative safety data to help researchers compare trends across locations and age groups.

**Highlights**
- Persona chat experience routed through OpenRouter-compatible models (default: `gpt-4o-mini`).
- Sidebar controls for persona selection, city and age filters, and model overrides.
- Streaming conversation history, transcript download, and lightweight memory summarization.
- Guardrails for unsafe content, PII filtering, and sentiment-aware responses.
- Every reply cites at least one vetted resource via Markdown links drawn from `data/city_resources.json`, spanning official reports, police social media feeds, and curated Reddit community conversations.

Problem & Solution
------------------
Cities collect large volumes of safety data, but frontline insights from women often stay fragmented across datasets, help-line reports, and social media anecdotes. That gap makes it hard for researchers and civic teams to understand how policies translate into lived experience.

This prototype stitches those perspectives together: synthetic personas surface real scenarios grounded in official statistics, verified advisories, and moderated community stories. The persona chat plus analytics dashboard gives teams a single space to hear context, inspect trends, and spot gaps that demand policy follow-up.

How It Works
------------
- Loads synthetic personas, sentiment baselines, and safety metrics, then assembles a first-person system prompt tailored to the selected city and demographics.
- Injects vetted source snippets—including government briefs, police updates, and Reddit community discussions—so personas can cite evidence and flag anecdotal context explicitly.
- Calls OpenRouter-hosted models (default `gpt-4o-mini`) with conversation history, guardrails, and persona memory to generate grounded responses.
- Summarises each exchange into rolling memory plus an exportable transcript, helping researchers tag patterns or share anonymised field notes.
- Lets you explore illustrative safety indicators by city and age group with interactive Plotly charts to corroborate or question themes raised in chat.

Getting Started
---------------
**Prerequisites**
- Python 3.10 or 3.11.
- `pip` and a shell that can export environment variables.
- An OpenRouter API key (free tier available at [openrouter.ai](https://openrouter.ai/)).

**Clone & Install**
```bash
git clone <repo-url>
cd women_safety_ai
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Configuration
-------------
The app loads secrets from `environment/.env` if present; otherwise it reads from the active shell environment.

```
environment/.env
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_APP_NAME=Women Safety Persona Chat     # optional, appears in OpenRouter logs
OPENROUTER_SITE_URL=https://example.org/research   # optional, referer for rate limiting
```

Always exclude `environment/.env` from version control and rotate the key if it leaks.

Running The App
---------------
```bash
source .venv/bin/activate
export OPENROUTER_API_KEY=sk-or-...   # omitted if stored in environment/.env
streamlit run app.py
```

Streamlit prints a local URL (default `http://localhost:8501` or `8502`). Leave the terminal open while testing and press `Ctrl+C` to stop the server.

Using The UI
------------
1. **Select Persona** – choose a persona from the sidebar to load demographics and top-level traits.  
2. **Filter Analytics** – optionally filter the dashboard by city or age group.  
3. **Pick Model** – supply any OpenRouter model slug (e.g., `openai/gpt-4o-mini`, `anthropic/claude-3-haiku`).  
4. **Chat** – enter safety scenarios, questions, or “what-if” prompts. The persona replies using contextual memory, sentiment hints, and weaves in at least one cited resource—whether a government brief, trusted social feed, or moderated Reddit discussion—per answer.  
5. **Download Transcript** – export the conversation from the bottom of the chat tab for research notes.

Analytics Tab
-------------
- Visualizes perceived safety scores by city and age group using the sample CSV in `data/safety_index.csv`.  
- Use filters to drill into specific demographics. Replace the CSV with official NCRB/NFHS/SafeCity datasets for real studies.

Tests
-----
```bash
pytest
```

The test suite validates persona prompt assembly and chart utilities. Extend it when adding new guardrails or data loaders.

Troubleshooting
---------------
- **Missing data files** – ensure you run the app from within `women_safety_ai/` or keep the repository structure intact. The loaders use absolute paths derived from `app.py`.  
- **Authentication fallback message** – confirm `OPENROUTER_API_KEY` is available in the environment.  
- **Model errors** – check the Streamlit logs for HTTP status codes. Invalid model slugs or exhausted quotas will trigger the fallback message.  
- **Watchdog warning** – installing the optional `watchdog` package improves hot-reload performance but is not required.

Architecture
------------
- `app.py` – Streamlit entry point wiring personas, chat history, analytics, and guardrails.  
- `utils/llm_client.py` – OpenRouter REST client and environment loader.  
- `utils/personality_builder.py` – persona prompt assembly.  
- `utils/memory.py` – rolling conversation memory and summary helper.  
- `utils/guardrails.py` – sanitization and postprocessing filters.  
- `utils/charts.py` – pandas/Plotly helpers for the analytics tab.
- `data/city_resources.json` – curated external links (official datasets, advisories, police social media, and moderated Reddit threads) personas cite.

Data & Sources
--------------
- **Core & national** – synthetic `data/personas.json`, `data/sentiment_profiles.json`, and `data/safety_index.csv` (illustrative scaffold) plus [NCRB Crime in India 2022](https://www.ncrb.gov.in/en/crime-india) and [Government Safe City programme](http://india.gov.in/spotlight/safe-city-project).
- **Delhi** – [Delhi crime overview](https://en.wikipedia.org/wiki/Delhi#Crime), [Delhi Police Facebook updates](https://www.facebook.com/DelhiPoliceOfficial), and a moderated Reddit account of neighbourhood harassment ([thread](https://www.reddit.com/r/delhi/comments/1hjq36g/help_my_neighbour_has_been_seually_harassing/)).
- **Lucknow** – [Lucknow safety profile](https://en.wikipedia.org/wiki/Lucknow#Crime), [1090 Women Power Line advisories](https://www.facebook.com/1090WomenPowerLine), and a Reddit collaboration call for One Stop Centres ([thread](https://www.reddit.com/r/lucknow/comments/1n76uru/calling_ngos_researchers_advocates_in_lucknow/)).
- **Pune** – [Pune law and order summary](https://en.wikipedia.org/wiki/Pune#Law_and_order), [Pune City Police briefings](https://www.facebook.com/PuneCityPolice), and a Reddit reaction to the Swargate assault case ([thread](https://www.reddit.com/r/pune/comments/1iypd74/shame_the_swar_gate_rape_crime/)).
- **Jaipur** – [Jaipur policing snapshot](https://en.wikipedia.org/wiki/Jaipur#Law_and_order), [Jaipur Police advisories](https://www.facebook.com/JaipurPolice), and a Reddit discussion on night-time safety gaps ([thread](https://www.reddit.com/r/jaipur/comments/1mzqze2/street_dogs_have_taken_over_my_colony_in_jaipur/)).
- **Bengaluru** – [Bengaluru law and order overview](https://en.wikipedia.org/wiki/Bangalore#Law_and_order), [Bengaluru City Police bulletins](https://www.facebook.com/BlrCityPolice), and a Reddit account of harassment at food distribution points ([thread](https://www.reddit.com/r/bangalore/comments/1jxz5sr/women_cant_even_collect_food_without_being_messed/)).

Dummy personas, sentiment profiles, safety scores, and citation resources live in `data/`. Swap them with vetted sources before citing results. Keep any sensitive data outside version control. Update `data/city_resources.json` whenever you need fresh links, official advisories, or trusted social channels (including carefully moderated Reddit threads) the personas should reference, and note when a source reflects anecdotal rather than official evidence.

Ethics & Privacy
----------------
This prototype works with synthetic personas and aggregate metrics only. It refuses requests for explicit or identifying information and should never be used as a substitute for on-the-ground safety interventions. Validate insights with real community stakeholders before acting on them.
