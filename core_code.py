import warnings
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

import whisper
import os
from pydub import AudioSegment
import tkinter as tk
from tkinter import filedialog, messagebox
import tempfile
import threading
import sounddevice as sd
import wave
import itertools

app = tk.Tk()
app.withdraw()  

try:
    model = whisper.load_model("small")  # Changed from base to small for better accuracy
except Exception as e:
    messagebox.showerror("Model Load Error", f"Whisper model failed to load:\n{e}")
    app.destroy()
    raise SystemExit

app.deiconify()  
recording = False
frames = []
stream = None

def transcribe_audio(file_path):
    temp_wav_path = None
    if not file_path.endswith(".wav"):
        try:
            audio = AudioSegment.from_file(file_path)
        except Exception as e:
            messagebox.showerror("Audio Error", f"Unable to load audio: {e}")
            return ""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
            temp_wav_path = tmpfile.name
        audio.export(temp_wav_path, format="wav")
        file_path_to_transcribe = temp_wav_path
    else:
        file_path_to_transcribe = file_path

    try:
        # load audio for language detection (optional, not really needed if forcing language)
        audio_data = whisper.load_audio(file_path_to_transcribe)
        audio_data = whisper.pad_or_trim(audio_data)
        mel = whisper.log_mel_spectrogram(audio_data).to(model.device)
        detect_result = model.detect_language(mel)
        detected_lang = max(detect_result[1], key=detect_result[1].get)  # Get language with highest probability
        print(f"Detected Language: {detected_lang}")  # Optional: print to console for debugging

        # Use the detected language automatically
        result = model.transcribe(file_path_to_transcribe, language=detected_lang, beam_size=5, temperature=[0.0, 0.2])

        if isinstance(result, dict) and result.get("text"):
            return result["text"]
        else:
            raise ValueError("Transcription failed or returned empty result.")
    except Exception as e:
        raise e
    finally:
        if temp_wav_path and os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)


def start_loading_animation():
    loading_states = itertools.cycle(["Transcribing   ", "Transcribing.  ", "Transcribing.. ", "Transcribing..."])
    def animate():
        if not getattr(loading_label, 'animating', False):
            loading_label.config(text="")
            return
        status = next(loading_states)
        loading_label.config(text=status)
        loading_label.after(400, animate)
    loading_label.animating = True
    animate()

def stop_loading_animation():
    loading_label.animating = False
    loading_label.config(text="")

def transcribe_in_thread(file_path):
    try:
        status_label.config(text="")
        start_loading_animation()
        text_output.config(state=tk.NORMAL)
        transcribed_text = transcribe_audio(file_path)
        text_output.delete("1.0", tk.END)
        text_output.insert(tk.END, transcribed_text)
        text_output.config(state=tk.DISABLED)
        stop_loading_animation()
        status_label.config(text="Transcription completed.", fg="#107c10")
    except Exception as e:
        stop_loading_animation()
        status_label.config(text="Error during transcription.", fg="#a80000")
        messagebox.showerror("Error", str(e))
    finally:
        if file_path.startswith(tempfile.gettempdir()) and os.path.exists(file_path):
            os.remove(file_path)

def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav *.m4a")])
    if file_path:
        threading.Thread(target=transcribe_in_thread, args=(file_path,), daemon=True).start()

def audio_callback(indata, frames_count, time, status):
    global frames
    frames.append(indata.copy())

def start_recording():
    global recording, frames, stream
    if recording:
        return
    frames = []
    try:
        stream = sd.InputStream(samplerate=44100, channels=1, dtype='int16', callback=audio_callback)
        stream.start()
        recording = True
        status_label.config(text="Recording...", fg="#ff8c00")
        record_button.config(text="■ Stop Recording", bg="#a4262c", activebackground="#911f27", fg="white")
    except Exception as e:
        messagebox.showerror("Recording Error", f"Cannot start recording: {e}")

def stop_recording():
    global recording, stream
    if not recording:
        return
    try:
        stream.stop()
        stream.close()
    except Exception as e:
        messagebox.showerror("Recording Error", f"Error stopping recording: {e}")
    recording = False
    record_button.config(text="🎙️ Record Audio", bg="#0078d7", activebackground="#005a9e", fg="white")
    status_label.config(text="Recording stopped. Processing...", fg="#0078d7")

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
        temp_wav_path = tmpfile.name
    wf = wave.open(temp_wav_path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(44100)
    wf.writeframes(b''.join([frame.tobytes() for frame in frames]))
    wf.close()

    threading.Thread(target=transcribe_in_thread, args=(temp_wav_path,), daemon=True).start()

def toggle_recording():
    if recording:
        stop_recording()
    else:
        start_recording()

def save_text():
    text = text_output.get("1.0", tk.END)
    if not text.strip():
        messagebox.showinfo("Empty", "No text to save.")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if file_path:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text)
            messagebox.showinfo("Saved", f"Transcription saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")

# ---------------- GUI -------------------

app.title("Speech-to-Text Whisper")
app.geometry("800x650")
app.configure(bg="#f3f2f1")
app.resizable(True, True)

shadow_frame = tk.Frame(app, bg="#d1d1d1")
shadow_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=768, height=608)

container = tk.Frame(app, bg="#ffffff", bd=0)
container.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=760, height=600)

title_label = tk.Label(container, text="🎤 Speech-to-Text Transcription",
                       font=("Segoe UI", 26, "bold"), fg="#323130", bg="white")
title_label.pack(pady=(30, 25))

button_frame = tk.Frame(container, bg="white")
button_frame.pack(pady=(0, 30))

btn_style = {
    "font": ("Segoe UI", 13, "bold"),
    "bd": 0,
    "width": 22,
    "relief": tk.FLAT,
    "cursor": "hand2",
    "padx": 10,
    "pady": 12,
}

def on_enter_btn(e):
    e.widget['bg'] = '#106ebe'

def on_leave_btn(e):
    if e.widget == record_button and recording:
        e.widget['bg'] = '#a4262c'
    elif e.widget == record_button:
        e.widget['bg'] = '#0078d7'
    elif e.widget == save_button:
        e.widget['bg'] = '#107c10'
    else:
        e.widget['bg'] = '#0078d7'

browse_button = tk.Button(button_frame, text="📁 Browse Audio File", command=select_file,
                          bg="#0078d7", fg="white", activebackground="#106ebe", **btn_style)
browse_button.grid(row=0, column=0, padx=12)
browse_button.bind("<Enter>", on_enter_btn)
browse_button.bind("<Leave>", on_leave_btn)

record_button = tk.Button(button_frame, text="🎙️ Record Audio", command=toggle_recording,
                          bg="#0078d7", fg="white", activebackground="#106ebe", **btn_style)
record_button.grid(row=0, column=1, padx=12)
record_button.bind("<Enter>", on_enter_btn)
record_button.bind("<Leave>", on_leave_btn)

save_button = tk.Button(button_frame, text="💾 Save Transcript", command=save_text,
                        bg="#107c10", fg="white", activebackground="#0b610b", **btn_style)
save_button.grid(row=0, column=2, padx=12)
save_button.bind("<Enter>", on_enter_btn)
save_button.bind("<Leave>", on_leave_btn)

status_label = tk.Label(container, text="", font=("Segoe UI", 13, "italic"), fg="#605e5c", bg="white")
status_label.pack(pady=(0, 10))

loading_label = tk.Label(container, text="", font=("Segoe UI", 13, "italic"), fg="#0078d7", bg="white")
loading_label.pack()

text_container = tk.Frame(container, bg="#e1dfdd", bd=0)
text_container.pack(padx=20, pady=(20, 25), fill=tk.BOTH, expand=True)

text_output = tk.Text(text_container, wrap="word",
                      font=("Nirmala UI", 14), bg="#faf9f8", fg="#201f1e",
                      relief=tk.FLAT, bd=0, insertbackground="#0078d7")
text_output.pack(fill=tk.BOTH, expand=True)
text_output.config(state=tk.DISABLED)

app.mainloop()
