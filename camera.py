import threading
import av
import mediapipe as mp
from streamlit_webrtc import VideoProcessorBase

_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)


class PresenceProcessor(VideoProcessorBase):
    """Measures % of frames where the face is visible and facing the screen."""

    def __init__(self):
        self.total = 0
        self.forward = 0
        self.frames = 0
        self.lock = threading.Lock()

    def recv(self, frame):
        img = frame.to_ndarray(format="rgb24")
        self.frames += 1
        if self.frames % 3 == 0:  # process every 3rd frame to stay fast
            facing = False
            res = _mesh.process(img)
            if res.multi_face_landmarks:
                lm = res.multi_face_landmarks[0].landmark
                width = max(lm[454].x - lm[234].x, 1e-6)
                ratio = (lm[1].x - lm[234].x) / width
                facing = 0.4 < ratio < 0.6
            with self.lock:
                self.total += 1
                self.forward += int(facing)
        return av.VideoFrame.from_ndarray(img, format="rgb24")

    def pop_score(self):
        """Return face-forward % since last call, then reset. None if no frames."""
        with self.lock:
            if self.total == 0:
                return None
            score = round(self.forward / self.total * 100)
            self.total = self.forward = 0
            return score
