import streamlit as st
import time
import os
from datetime import datetime

st.set_page_config(page_title="Alarm Clock ⏰", page_icon="⏰", layout="centered")

st.markdown(
    """
    <style>
    .timer-display {
        text-align: center;
        font-size: 90px;
        font-weight: 700;
        color: #FF4B4B;
        font-family: 'Courier New', monospace;
        padding: 20px 0;
    }
    .timer-label {
        text-align: center;
        font-size: 20px;
        color: #888;
        margin-bottom: -10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("⏰ Alarm Clock / Countdown Timer")
st.write("Set a countdown timer, name it, and get notified with sound when time's up!")

# ---- Session state defaults ----
if "minutes" not in st.session_state:
    st.session_state.minutes = 0
if "seconds" not in st.session_state:
    st.session_state.seconds = 10
if "history" not in st.session_state:
    st.session_state.history = []


def set_preset(m):
    st.session_state.minutes = m
    st.session_state.seconds = 0


# ---- Quick presets ----
st.subheader("Quick Presets")
p1, p2, p3, p4 = st.columns(4)
with p1:
    st.button("1 min", on_click=set_preset, args=(1,), use_container_width=True)
with p2:
    st.button("5 min", on_click=set_preset, args=(5,), use_container_width=True)
with p3:
    st.button("10 min", on_click=set_preset, args=(10,), use_container_width=True)
with p4:
    st.button("25 min 🍅", on_click=set_preset, args=(25,), use_container_width=True)

# ---- Manual input ----
label = st.text_input("Timer name (optional)", placeholder="e.g. Tea break, Study session")

col1, col2 = st.columns(2)
with col1:
    minutes = st.number_input("Minutes", min_value=0, max_value=180, step=1, key="minutes")
with col2:
    seconds = st.number_input("Seconds", min_value=0, max_value=59, step=1, key="seconds")

sound_on = st.checkbox("🔊 Play sound when done", value=True)

total_seconds = int(minutes) * 60 + int(seconds)

start = st.button("▶️ Start Timer", type="primary", use_container_width=True)

label_placeholder = st.empty()
placeholder = st.empty()
progress_placeholder = st.empty()

if start:
    if total_seconds <= 0:
        st.warning("Please set a time greater than 0 seconds.")
    else:
        if label:
            label_placeholder.markdown(f"<div class='timer-label'>{label}</div>", unsafe_allow_html=True)

        remaining = total_seconds
        while remaining >= 0:
            mins_left, secs_left = divmod(remaining, 60)
            elapsed_pct = (total_seconds - remaining) / total_seconds
            placeholder.markdown(
                f"<div class='timer-display'>{mins_left:02d}:{secs_left:02d}</div>",
                unsafe_allow_html=True,
            )
            progress_placeholder.progress(elapsed_pct)
            time.sleep(1)
            remaining -= 1

        placeholder.empty()
        progress_placeholder.empty()
        label_placeholder.empty()

        st.success(f"⏰ {label or 'Timer'} finished!")
        st.balloons()

        # Save to history
        st.session_state.history.insert(
            0,
            {
                "label": label or "Untitled",
                "duration": f"{minutes:02d}:{seconds:02d}",
                "finished_at": datetime.now().strftime("%I:%M %p"),
            },
        )

        if sound_on:
            audio_file = "alaram.mp3"
            if os.path.exists(audio_file):
                with open(audio_file, "rb") as f:
                    st.audio(f.read(), format="audio/mp3", autoplay=True)
            else:
                st.warning(
                    "⚠️ 'alaram.mp3' not found in the app folder. "
                    "Add it next to app.py (same folder) to enable sound."
                )

# ---- History sidebar ----
with st.sidebar:
    st.subheader("📜 Timer History")
    if st.session_state.history:
        for item in st.session_state.history[:10]:
            st.write(f"**{item['label']}** — {item['duration']} (done at {item['finished_at']})")
        if st.button("Clear history"):
            st.session_state.history = []
            st.rerun()
    else:
        st.caption("No timers completed yet.")