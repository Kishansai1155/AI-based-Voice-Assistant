# AI-based-Voice-Assistant
A smart and lightweight voice-controlled assistant built using Python, Flask, and Speech Recognition libraries. This project performs various tasks through voice commands, such as answering questions, telling the time/date, searching Wikipedia, checking the weather, opening websites, and more — all via a simple web interface.
🚀 Features
🎙️ Voice Input & Output: Captures user voice using a microphone and responds using text-to-speech (TTS).

⌛ Tells Current Time and Date

🌐 Wikipedia Integration: Answers general knowledge questions using Wikipedia summary extraction.

☁️ Weather Reports (using OpenWeatherMap API – configurable)

🔍 Web Browsing: Opens Google or YouTube on voice command.

➗ Basic Calculator: Evaluates math expressions using voice.

🧠 Natural Command Processing: Understands common language queries like "What is the time?", "Tell me about AI", etc.

🌍 Flask Web Interface: Simple front-end for live testing and interaction.

🧵 Multithreading Support: Runs speech output in a separate thread for non-blocking UI.

🛠️ Tech Stack
Python 3

Flask – Web server

SpeechRecognition – For capturing and converting voice to text

pyttsx3 – Offline TTS engine

Wikipedia API – For querying general knowledge

OpenWeatherMap API – Weather data (requires API key)

Threading – For background voice synthesis

