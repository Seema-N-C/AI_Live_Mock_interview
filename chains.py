import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from prompts import FIRST_Q_PROMPT, EVAL_PROMPT, REPORT_PROMPT

load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.4)
json_llm = llm.bind(response_format={"type": "json_object"})


def first_question(role: str, resume_text: str) -> str:
    chain = FIRST_Q_PROMPT | llm
    return chain.invoke({"role": role, "resume_text": resume_text or "(none)"}).content.strip()


def evaluate_and_next(role, resume_text, history, question, answer) -> dict:
    """history = list of (question, answer). Returns score, feedback, next_question."""
    hist_text = "\n".join(f"Q: {q}\nA: {a}" for q, a in history[-6:]) or "(first answer)"
    chain = EVAL_PROMPT | json_llm
    raw = chain.invoke({
        "role": role,
        "resume_text": resume_text or "(none)",
        "history": hist_text,
        "question": question,
        "answer": answer,
    }).content
    try:
        data = json.loads(raw)
        return {
            "score": max(0, min(10, int(data.get("score", 5)))),
            "feedback": str(data.get("feedback", "")),
            "next_question": str(data.get("next_question", "Tell me more about your projects.")),
        }
    except Exception:
        return {"score": 5, "feedback": "Could not parse evaluation.",
                "next_question": "Can you tell me more about a project you built?"}


def generate_report(role, turns, averages) -> str:
    transcript = "\n\n".join(
        f"Q{i+1}: {t['question']}\nAnswer: {t['answer']}\n"
        f"Tech {t['tech_score']}/10 | Comm {t['comm_score']} | Fillers {t['fillers']} | "
        f"WPM {t['wpm']} | Face-forward {t['presence']}%\nFeedback: {t['feedback']}"
        for i, t in enumerate(turns)
    )
    chain = REPORT_PROMPT | llm
    return chain.invoke({"role": role, "transcript": transcript,
                         "averages": json.dumps(averages)}).content
