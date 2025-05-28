# 📘 Advanced Q&A Evaluator API

A Flask-based API server that uses Google's Gemini models to answer user questions and evaluate the quality of the generated responses using both NLP metrics (ROUGE, BLEU) and LLM-as-a-Judge technique.

---

## 🚀 Features

- ✅ Answer generation using Gemini LLM
- 📊 Advanced evaluation using:
  - ROUGE (1, 2, L)
  - BLEU score
  - LLM-as-a-Judge (structured JSON verdict)
- 🛡️ Input validation and error handling
- 🧠 Generates reference answers for comparison
- 🔁 Clean and reusable code structure with decorators
- 🌐 CORS-enabled for cross-origin requests

---

## 🔧 Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/advanced-qa-evaluator.git
cd advanced-qa-evaluator
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your `.env` file

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_google_gemini_api_key_here
FLASK_ENV=development
PORT=5000
```

---

## 🏃 Getting Started

### Run the API server

```bash
python api_server.py
```

### Test with `curl` or Postman

#### 🔍 Ask a Question

```bash
curl -X POST http://localhost:5000/api/ask \
-H "Content-Type: application/json" \
-d '{"question": "What is the capital of France?"}'
```

#### ❤️ Health Check

```bash
curl http://localhost:5000/api/health
```

---

## 📁 Project Structure

```text
.
├── api_server.py          # Flask server with endpoints and evaluator initialization
├── ass.py                 # AdvancedQAEvaluator class with answer + evaluation logic
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (GEMINI_API_KEY, FLASK_ENV, etc.)
└── README.md              # This file
```

---

## 🧪 API Endpoints

### `POST /api/ask`

**Request Body:**
```json
{
  "question": "Your question here"
}
```

**Response Example:**
```json
{
  "question": "What is AI?",
  "answer": "...",
  "evaluation": {
    "llm_judge_verdict": "GOOD",
    "score": 8,
    "reasoning": "Detailed and informative...",
    "strengths": [...],
    "missing_elements": [...],
    "clarity": 9,
    "accuracy": 8,
    "completeness": 7,
    "judge_confidence": 8
  },
  "timestamp": "2025-05-28T12:00:00Z"
}
```

---

### `GET /api/health`

Returns status of the server and evaluator.

---

## 🧠 Evaluation Strategy

### ✅ ROUGE & BLEU
- Measures lexical similarity between the generated and reference answers.

### 🤖 LLM-as-a-Judge
- Uses Gemini to rate the quality of answers based on:
  - Accuracy
  - Completeness
  - Clarity
  - Depth
  - Usefulness

---


## 👨‍💻 Author


- **Shiv Patel**

---
![Screenshot 2025-05-28 113634](https://github.com/user-attachments/assets/0e6ca92f-65e3-4fb1-871b-a7e9bfee4a6d)

![Screenshot 2025-05-28 113655](https://github.com/user-attachments/assets/93c79e3f-d688-4fe8-b37b-375a43409f02)


