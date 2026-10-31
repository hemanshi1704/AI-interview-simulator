import json
from openai import OpenAI
from app.config import get_settings

settings = get_settings()
_client = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=settings.openai_api_key)
    return _client


def generate_questions(resume_text: str, target_role: str, num_questions: int = 5) -> list[dict]:
    """Returns a list of {question_text, category} dicts."""
    prompt = f"""You are a senior technical interviewer. Based on the candidate's resume and
their target role, generate {num_questions} interview questions.

Target role: {target_role}

Resume text:
\"\"\"{resume_text[:6000]}\"\"\"

Mix technical, behavioral, and role-specific questions relevant to the resume's actual
skills/projects. Respond ONLY with a JSON array like:
[{{"question_text": "...", "category": "technical"}}, ...]
Categories must be one of: technical, behavioral, communication."""

    client = get_client()
    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    content = response.choices[0].message.content.strip()
    content = content.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(content)


def evaluate_answer(question: str, answer: str, category: str, target_role: str) -> dict:
    """Returns {technical_score, communication_score, feedback} — scores 0-10."""
    prompt = f"""You are an expert interview evaluator for a {target_role} position.

Question ({category}): {question}
Candidate's answer (transcribed from speech, may have minor grammar noise): {answer}

Score the answer from 0-10 on:
- technical_score: correctness, depth, relevance of content
- communication_score: clarity, structure, confidence of delivery

Then give 2-3 sentences of specific, actionable feedback.

Respond ONLY with JSON: {{"technical_score": 0-10, "communication_score": 0-10, "feedback": "..."}}"""

    client = get_client()
    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    content = response.choices[0].message.content.strip()
    content = content.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(content)
