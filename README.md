# AI Live Mock Interview

An AI-powered mock interview platform that asks interview questions in real time, evaluates your answers, and gives instant feedback to help candidates prepare for technical and HR rounds.



![Demo](screenshots/demo.gif)



## Features

- Live question-and-answer interview with an AI interviewer
- Role-based questions (e.g. Python, GenAI, Data, HR) [edit]
- Voice or text answers with speech-to-text [edit]
- Real-time answer evaluation and scoring
- Follow-up questions based on your previous answers
- Final feedback report with strengths, weak areas and improvement tips
- Interview history and progress tracking [edit]

## Tech Stack

- **Language:** Python
- **UI:** Streamlit
- **LLM:** OpenAI 
- **Speech:**  Whisper 
- **Resume parsing:** PyPDF2
- **Data:**  SQLite 

## How It Works

Select Role → (Upload Resume) → AI asks question → Candidate answers (voice/text) → LLM evaluates → Follow-up question → Final feedback report



![Architecture](screenshots/architecture.png)


## Project Structure

| File | Purpose |
|------|---------|
| `app.py` | Main entry point |
| [`interviewer.py`] | Generates questions and follow-ups |
| [`evaluator.py`] | Scores answers and gives feedback |
| [`speech.py`] | Speech-to-text / text-to-speech |
| [`report.py`] | Final feedback report |
| `config.py` | Settings (API keys loaded from `.env`) |


## Usage

1. Choose a role and difficulty level
2. Start the interview and answer each question
3. Get instant feedback after every answer
4. Review your final score and report

## Future Improvements

- Video-based interview with body language and confidence analysis
- Multi-language support
- Company-specific interview modes
- Cloud deployment

## Author

**Seema N C** · [GitHub](https://github.com/Seema-N-C)
