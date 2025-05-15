# 🎤 Speech-to-Text Whisper

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](https://opensource.org/licenses/MIT)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen)](https://github.com/)

A simple and user-friendly desktop application that converts speech to text using OpenAI's Whisper model.  
It supports transcribing audio files and recording audio directly from the microphone with automatic language detection.

---

## ✨ Features

- 🎧 Transcribe audio files (MP3, WAV, M4A).
- 🎙️ Record audio from microphone and transcribe.
- 🌐 Automatic language detection.
- 💾 Save transcriptions as text files.
- 🖥️ User-friendly GUI built with Tkinter.
- ⏳ Loading animation during transcription.
- ⚠️ Basic error handling for audio and transcription issues.

---

## 🚀 Installation

1. Clone or download the repository.

2. Install required Python packages:

```bash
pip install whisper pydub sounddevice
```

> Note: `tkinter` is usually included with Python. For audio conversion, ensure FFmpeg is installed and added to your system PATH.

---

## 🛠️ Usage

Run the app with:

```bash
python core_code.py
```

- Use **Browse Audio File** to select an audio file for transcription.
- Use **Record Audio** to start/stop recording from your microphone.
- Use **Save Transcript** to save the transcribed text to a file.
- Transcription results appear in the text area with status updates.

---

## 📝 Notes

- The app uses the Whisper "small" model for better accuracy.
- Temporary WAV files are created and cleaned up automatically.
- Errors during loading, recording, or transcription are shown via message boxes.

---
## 📄 License

This project is open source and free to use.
