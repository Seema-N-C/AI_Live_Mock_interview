import uuid
import streamlit as st
from streamlit_webrtc import webrtc_streamer

from resume import extract_resume
from chains import first_question, evaluate_and_next, generate_report
from memory_store import init_db, save_turn, get_turns, get_averages
from voice import transcribe, speak
from metrics import analyze
from camera import PresenceProcessor

st.set_page_config(page_title="AI Mock Interview Coach", page_icon="🎤", layout="wide")
init_db()

ROLES = ["Python Developer", "Backend Developer", "GenAI Intern",
         "Data Analyst", "Frontend Developer"]

ss = st.session_state
defaults = {
    "sid": uuid.uuid4().hex[:8], "messages": [], "history": [],
    "current_q": None, "started": False, "ended": False, "report": None,
    "resume_text": "", "resume_name": None, "audio_n": 0, "pending_audio": None,
}
for k, v in defaults.items():
    ss.setdefault(k, v)

# ---------------- Sidebar ----------------
st.sidebar.header("Interview setup")
name = st.sidebar.text_input("Your name", "Demo")
role = st.sidebar.selectbox("Role you're interviewing for", ROLES)

resume_file = st.sidebar.file_uploader("Upload resume (PDF)", type="pdf")
if resume_file and ss.resume_name != resume_file.name:
    ss.resume_text = extract_resume(resume_file)
    ss.resume_name = resume_file.name
    st.sidebar.success(f"Resume loaded ({len(ss.resume_text)} chars)")
    if not ss.resume_text:
        st.sidebar.warning("No text found. Is this a scanned PDF?")

if st.sidebar.button("Start / Restart Interview", type="primary"):
    ss.sid = uuid.uuid4().hex[:8]
    ss.history, ss.ended, ss.report = [], False, None
    with st.spinner("Preparing your first question..."):
        q = first_question(role, ss.resume_text)
    ss.messages = [{"role": "assistant", "content": q}]
    ss.current_q = q
    ss.pending_audio = speak(q)
    ss.started = True

if st.sidebar.button("End interview") and ss.started:
    ss.ended = True

st.sidebar.markdown("**Camera** (video is processed locally, not stored)")
with st.sidebar:
    ctx = webrtc_streamer(
        key="cam",
        video_processor_factory=PresenceProcessor,
        media_stream_constraints={"video": True, "audio": False},
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    )


# ---------------- Helpers ----------------
def overall_score(avg: dict):
    parts = [(avg.get("tech"), 0.5), (avg.get("comm"), 0.3),
             (None if avg.get("presence") is None else avg["presence"] / 10, 0.2)]
    parts = [(v, w) for v, w in parts if v is not None]
    if not parts:
        return None
    return round(sum(v * w for v, w in parts) / sum(w for _, w in parts), 1)


def handle_answer(text: str, metrics):
    presence = None
    if ctx and ctx.video_processor:
        presence = ctx.video_processor.pop_score()

    with st.spinner("Evaluating..."):
        result = evaluate_and_next(role, ss.resume_text, ss.history, ss.current_q, text)

    save_turn(ss.sid, role, ss.current_q, text, result["score"], result["feedback"],
              metrics, presence)
    ss.history.append((ss.current_q, text))

    meta = ""
    if metrics:
        meta = (f"WPM {metrics['wpm']} | Fillers {metrics['fillers']} | "
                f"Pauses {metrics['pauses']} | Comm {metrics['comm_score']}/10")
    if presence is not None:
        meta += f" | Face-forward {presence}%"

    ss.messages.append({"role": "user", "content": text, "meta": meta})
    ss.messages.append({
        "role": "assistant",
        "content": f"**Score: {result['score']}/10** — {result['feedback']}\n\n"
                   f"**Next question:** {result['next_question']}",
    })
    ss.current_q = result["next_question"]
    ss.pending_audio = speak(result["next_question"])
    ss.audio_n += 1  # resets the audio widget
    st.rerun()


# ---------------- Main ----------------
st.title("🎤 AI Mock Interview Coach")

if not ss.started:
    st.info("Pick a role, upload your resume (optional), and click **Start / Restart Interview**.")
    st.stop()

for m in ss.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if m.get("meta"):
            st.caption(m["meta"])

if ss.ended:
    turns = get_turns(ss.sid)
    if not turns:
        st.warning("Answer at least one question first.")
        st.stop()
    avg = get_averages(ss.sid)
    if ss.report is None:
        with st.spinner("Writing your report..."):
            ss.report = generate_report(role, turns, avg)
    st.header("📊 Final report")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Overall", f"{overall_score(avg)}/10")
    c2.metric("Technical", f"{avg['tech']}/10")
    c3.metric("Communication", f"{avg['comm']}/10" if avg["comm"] is not None else "n/a")
    c4.metric("Face-forward", f"{avg['presence']}%" if avg["presence"] is not None else "n/a")
    st.markdown(ss.report)
    st.stop()

if ss.pending_audio:
    st.audio(ss.pending_audio, format="audio/mp3", autoplay=True)
    ss.pending_audio = None

audio = st.audio_input("🎙️ Record your answer", key=f"audio_{ss.audio_n}")
if audio and st.button("Submit voice answer"):
    with st.spinner("Listening..."):
        text, segs = transcribe(audio.getvalue())
    if text:
        handle_answer(text, analyze(text, segs))
    else:
        st.warning("Could not hear anything. Try again.")

typed = st.chat_input("...or type your answer")
if typed:
    handle_answer(typed, None)
