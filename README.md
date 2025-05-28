# LLM-as-a-Judge Q&A Evaluator

Evaluates LLM-generated answers using Google Gemini API with NLP metrics.

## Setup

1.  `git clone <your_repository_url>`
2.  `pip install -r requirements.txt`
3.  Create `.env`: `GEMINI_API_KEY=your_api_key_here`
4.  `python api_server.py`

## API

*   `POST /api/ask`:  Question -> Answer, Evaluation
*   `GET /api/health`:  Service Status

## Deployment

Set `GEMINI_API_KEY` on your hosting platform.
