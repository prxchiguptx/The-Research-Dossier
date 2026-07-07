# The Research Dossier: Multi-Agent Intelligence Pipeline

A production-ready, stateful multi-agent research workflow built using **LangGraph**, **LangChain**, and **Streamlit**. The application automates technical domain deep-dives by orchestrating specialized AI agents using an explicit supervisor pipeline layout. It fetches live web data, strips out systemic noise, synthesizes a structured report, and filters it through a critical grading loop—all powered by Google's **Gemini 2.5 Flash** model.

## 🚀 Live Demo
Experience the active application on the cloud: **[Insert your Streamlit App URL here]**

---

## 🏗️ Multi-Agent Architecture & Workflow

The architecture transitions beyond simple single-prompt engineering by splitting the research lifecycle into 5 distinct computational phases coordinated via a shared state dictionary:

### Step 1 — Environment Setup
The codebase establishes a deterministic execution context via virtual environments (`.venv`), modular requirement sheets, and secure access tokens dynamically bound to the runtime via environment scopes.

### Step 2 — Custom Core Tools (`tools.py`)
Two discrete low-level tools execute information retrieval using the `@tool` optimization wrapper:
* **`web_search`**: Directly interfaces with the Tavily API layer to poll fresh, highly detailed, and ranked search nodes from across the web.
* **`scrape_url`**: Parses explicit remote address layers, processes unstructured HTML via document object navigation, and extracts clean, readable text bodies using `BeautifulSoup`.

### Step 3 — Specialized Agents & Components (`agents.py`)
This engine instantiates 4 processing entities configured with localized prompts:
1.  **Search Agent:** Tailored via `create_react_agent` and `AgentExecutor` to aggressively use the `web_search` toolkit.
2.  **Reader Agent:** Constructed using identical patterns but uniquely isolated to execute semantic parsing and deep processing over targeted payloads via `scrape_url`.
3.  **Writer Chain:** A structural synthesis pipeline built via LangChain Expression Language (LCEL) passing data through an immutable stack: `prompt | llm | StrOutputParser()`.
4.  **Critic Chain:** An independent semantic validation block built on LCEL that assesses the draft report against structural guidelines, providing a quantitative score and itemized grading feedback.

### Step 4 — Central Orchestration Supervisor (`pipeline.py`)
Acts as the central operational director. It wraps the entire sequence inside a foundational routine called `run_research_pipeline()`. This coordinator manages data handover across all components sequentially by updating and reading from a centralized state dictionary, writing logging blocks directly to the active console terminal at the completion of each micro-step.

### Step 5 — Presentation & Runtime User Interface (`app.py`)
The execution wrapper interfaces through an interactive Streamlit frontend. Users enter a research domain or prompt topic, watch the logs stream in live time across the step sequences, and view the final, structured dossier complete with automated critic feedback.

---

## 📱 Application Interface

Here is a visual breakdown of the research environment in action:

| 1. Input & Topic Initiation | 2. Agent Execution Sequence | 3. Final Evaluated Dossier |
| :---: | :---: | :---: |
| ![Input UI](images/1.png) | ![Logs Output](images/2.png) | ![Report View](images/3.png) |

---

## 📁 Repository Schema

```text
├── images/               # Production interface assets and layout previews
│   ├── 1.png             # UI Initialization view
│   ├── 2.png             # Active pipeline trace logs
│   └── 3.png             # Critic analysis & Markdown report payload
├── .env                  # Local deployment environment configuration parameters (Untracked)
├── .gitignore            # Strict tracking exclusion maps (.venv, __pycache__, local credentials)
├── agents.py             # Generative AI models initialization & runtime logic
├── app.py                # Presentation engine and interactive Streamlit UI
├── pipeline.py           # Supervisors layout orchestrating state dictionaries
├── tools.py              # Low-level functional tools execution parameters
└── requirements.txt      # Dependency manifest for environment synchronization
