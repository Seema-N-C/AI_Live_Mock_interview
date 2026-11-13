from langchain_core.prompts import ChatPromptTemplate

SYSTEM = """You are a professional interviewer for the role: {role}.

Candidate resume:
{resume_text}

Rules:
- Ask questions based on the candidate's actual projects, skills and experience.
- Mix resume-based questions with core fundamentals for the role.
- Ask ONE question at a time, keep it short and clear.
- If the previous answer was weak or vague, ask a follow-up before moving on.
- If the resume is empty, ask general questions for the role.
"""

FIRST_Q_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM + "\nGreet the candidate in one short line, then ask the first question. Plain text only."),
    ("human", "Start the interview."),
])

EVAL_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM + """
Conversation so far:
{history}

Evaluate the candidate's latest answer, then ask the next question.
Reply ONLY with JSON in exactly this format:
{{"score": <integer 0-10 for technical correctness and depth>,
  "feedback": "<2 short sentences: what was good and what was missing>",
  "next_question": "<the next interview question>"}}
"""),
    ("human", "Question: {question}\nCandidate answer: {answer}"),
])

REPORT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an interview coach writing a final feedback report for a fresher
interviewing for: {role}. Use markdown. Be honest, specific and encouraging.

Sections:
1. Overall summary (3 lines)
2. Technical strengths
3. Technical weak areas (topics to study)
4. Communication (use the speaking stats; do NOT claim to judge emotion or tone)
5. Presentation (face-forward % from camera, if available)
6. Top 3 action items for next week
"""),
    ("human", """Transcript with per-answer scores:
{transcript}

Averages:
{averages}"""),
])
