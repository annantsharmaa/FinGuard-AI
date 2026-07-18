# 🛡️ FinGuard AI

## Multi-Agent Compliance & Audit Assistant

FinGuard AI is an AI-powered financial document auditing system that analyzes invoices, contracts, and purchase orders to identify compliance issues, calculate risk scores, and generate audit reports.

The system combines deterministic compliance rules with a local LLM (Llama 3 via Ollama) to create an explainable and auditable AI workflow.

---

## ✨ Key Features

### 📄 Document Intelligence
- Supports PDF, DOCX, and TXT documents
- Automatic document classification
- Extracts structured information from financial documents

### ✅ Compliance Engine
Performs automated checks for:

- Missing signatures
- Missing invoice numbers
- Invalid GST information
- Incorrect payment terms
- Missing vendor details
- Amount calculation mismatches

### 📊 Explainable Risk Scoring

Risk scores are calculated using deterministic rules:

- 0-59 → Auto Cleared
- 60+ → Human Review Required

Every score has a transparent breakdown explaining why risk was assigned.

### 🤖 Local LLM Integration

Uses:

- Ollama
- Llama 3

The LLM is used only for:
- Generating readable explanations
- Detecting unusual policy language

The LLM does not decide compliance results or risk scores.

### 🔍 Audit Trail

Every action is logged:

- Document processing
- Compliance checks
- Risk calculations
- Agent actions
- Human approvals/rejections

---

# 🏗️ Architecture


```
                 Document Upload

                       |
                       ↓

              Document Processing

                       |
                       ↓

        ┌───────────────────────────┐
        │      Agent Pipeline        │
        └───────────────────────────┘

          ↓          ↓          ↓          ↓

      Parser   Compliance   Risk   Report Generator

                       |
                       ↓

                 SQLite Database

                       |
                       ↓

                 Audit Reports

                       |
                       ↓

              Ollama + Llama 3
```

---

# 🧠 Agent Workflow

## 1. Document Parser Agent

Responsible for:

- Extracting text
- Identifying document type
- Storing document metadata


## 2. Compliance Agent

Runs rule-based checks:

- Invoice validation
- Tax compliance
- Payment verification


## 3. Risk Agent

Calculates:

- Risk score
- Severity
- Review requirement


## 4. Report Agent

Generates:

- Audit summary
- Findings
- Recommendations


---

# 🛠️ Tech Stack

| Component | Technology |
|-|-|
| Language | Python |
| AI Framework | CrewAI |
| LLM Runtime | Ollama |
| Model | Llama 3 |
| Backend | Python Pipeline |
| UI | Streamlit |
| Database | SQLite |
| Document Parsing | PyPDF2, python-docx |
| Testing | unittest |

---

# 📂 Project Structure

```
agents/
    pipeline.py
    crew.py

compliance/
    rules.py

risk/
    scoring.py

parsing/
    extract.py
    classify.py

llm/
    ollama_client.py

db/
    schema.sql
    db.py
```

---

# 🚀 Installation

Clone repository:

```bash
git clone https://github.com/YOUR_USERNAME/FinGuard-AI.git

cd FinGuard-AI
```


Create environment:

```bash
python -m venv venv
```

Activate:

Linux:

```bash
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```


Install dependencies:

```bash
pip install -r requirements.txt
```

---

# 🦙 Setup Llama 3

Install Ollama:

https://ollama.com


Download model:

```bash
ollama pull llama3
```


Start Ollama:

```bash
ollama serve
```

---

# ▶️ Running the Application


Start Streamlit:

```bash
streamlit run app.py
```


---

# 🧪 Testing

Run:

```bash
python -m unittest tests.test_rules -v
```


Example:

```
9/9 tests passed
```

---

# 📊 Example Workflow

1. Upload invoice
2. Extract document information
3. Run compliance checks
4. Generate risk score
5. Review flagged documents
6. Export audit report


---

# 🔐 Responsible AI Design

FinGuard AI follows explainable AI principles:

- No LLM-generated compliance decisions
- Deterministic scoring
- Human approval for high-risk cases
- Complete audit history


---

# 🔮 Future Improvements

- OCR support for scanned documents
- PostgreSQL migration
- Authentication system
- Versioned compliance policies
- Cloud deployment
- Advanced fraud detection


---

# 👨‍💻 Author

**Annant Sharma**

B.Tech Computer Science Engineering

GitHub: YOUR_PROFILE_LINK

LinkedIn: YOUR_PROFILE_LINK
