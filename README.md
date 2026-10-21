# MetricMint

> A reliable AI assistant that helps analysts find company financial metrics, verify them from official reports, and avoid hallucinated answers.

## Problem
When analysing companies like Eternal (Zomato and Blinkit), Swiggy, Nykaa, and Info Edge, finding the right financial metrics is time consuming and data is spread across annual reports, shareholder letters, and other investor documents.

Companies often define metrics differently or don’t disclose them. AI chatbots may fill these gaps with made-up numbers, leading to inaccurate data and unreliable analysis.

MetricMint aims to solve this by finding answers directly from official company reports, showing the source and the company's definition of each metric, and clearly saying "not disclosed" when the information cannot be verified.

## Who it is for
- **Data analyst intern at a Bengaluru-based VC fund
- **Investment associate

## Signature feature
**Definition card**: Each metric answer includes its definition and direct quote from the original report. This helps analysts understand the context and compare metrics accurately across companies.


## Hardest problem (my interview story)
One of MetricMint’s main challenges is making sure the AI doesn’t guess when information is missing. I plan to test it with 100 questions, including 20 unanswerable ones, to check accuracy and how well it handles missing information. The goal is to reduce hallucinations using a confidence threshold and a refusal mechanism, ensuring answers are backed by reliable sources.

## Dataset
| Source | Link | Documents | Pages | Licence / terms |
|---|---|---|---|---|
| Eternal Ltd (Zomato, Blinkit): shareholders' letters, quarterly results, annual reports | https://www.eternal.com/investor-relations/results/ | <n> | <n> | Publicly released company filings from the investor relations page; used for research only |

## 10 real questions
See [docs/QUESTIONS.md](docs/QUESTIONS.md).

## Run it
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env                                 # Windows: copy .env.example .env
uvicorn app.main:app --reload
curl localhost:8000/health
```

## Live link
<Added in Week 2>
