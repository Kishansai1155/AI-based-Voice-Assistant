from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import os
import wikipedia
import requests
import json
from threading import Thread
import io
import base64

app = Flask(__name__)

class VoiceAssistant:
    def __init__(self):
        # Initialize text-to-speech engine
        self.tts_engine = pyttsx3.init()
        self.setup_tts()
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Adjust for ambient noise
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
    
    def setup_tts(self):
        """Configure text-to-speech settings"""
        voices = self.tts_engine.getProperty('voices')
        if voices:
            # Try to set a female voice if available
            for voice in voices:
                if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
        
        # Set speech rate and volume
        self.tts_engine.setProperty('rate', 180)
        self.tts_engine.setProperty('volume', 0.9)
    
    def speak(self, text):
        """Convert text to speech"""
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def listen(self):
        """Listen for audio input and convert to text"""
        try:
            with self.microphone as source:
                print("Listening...")
                # Listen for audio with timeout
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                
            # Recognize speech using Google's service
            text = self.recognizer.recognize_google(audio)
            return text.lower()
            
        except sr.WaitTimeoutError:
            return "timeout"
        except sr.UnknownValueError:
            return "unknown"
        except sr.RequestError as e:
            return f"error: {str(e)}"
    
    def get_time(self):
        """Get current time"""
        now = datetime.datetime.now()
        return now.strftime("The current time is %I:%M %p")
    
    def get_date(self):
        """Get current date"""
        now = datetime.datetime.now()
        return now.strftime("Today's date is %B %d, %Y")
    
    def search_wikipedia(self, query):
        """Search Wikipedia for information"""
        try:
            # Remove common command words
            search_terms = query.replace("search for", "").replace("tell me about", "").strip()
            result = wikipedia.summary(search_terms, sentences=2)
            return result
        except wikipedia.exceptions.DisambiguationError as e:
            return f"Multiple results found. Please be more specific. Options include: {', '.join(e.options[:3])}"
        except wikipedia.exceptions.PageError:
            return "Sorry, I couldn't find information about that topic."
        except Exception as e:
            return "Sorry, I encountered an error while searching."
    
    def get_weather(self, city="London"):
        """Get weather information (you'll need to sign up for a free API key)"""
        # This is a placeholder - you'll need to get a free API key from OpenWeatherMap
        api_key = "YOUR_API_KEY_HERE"
        
        if api_key == "YOUR_API_KEY_HERE":
            return "Weather service is not configured. Please add your OpenWeatherMap API key."
        
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            response = requests.get(url)
            data = response.json()
            
            if response.status_code == 200:
                temp = data['main']['temp']
                description = data['weather'][0]['description']
                return f"The weather in {city} is {description} with a temperature of {temp}°C"
            else:
                return "Sorry, I couldn't get the weather information."
        except:
            return "Sorry, I encountered an error while getting weather information."
    
    def process_command(self, command):
        """Process voice commands and return appropriate responses"""
        command = command.lower().strip()
        
        if not command or command in ["timeout", "unknown"]:
            return "I didn't catch that. Could you please repeat?"
        
        if command.startswith("error:"):
            return "There was an error with speech recognition. Please try again."
        
        # Greeting commands
        if any(word in command for word in ["hello", "hi", "hey"]):
            return "Hello! How can I help you today?"
        
        # Time commands
        elif any(word in command for word in ["time", "what time"]):
            return self.get_time()
        
        # Date commands
        elif any(word in command for word in ["date", "what date", "today"]):
            return self.get_date()
        
        # Wikipedia search
        elif any(phrase in command for phrase in ["search for", "tell me about", "what is", "who is"]):
            return self.search_wikipedia(command)
        
        # Weather commands
        elif "weather" in command:
            if "in" in command:
                city = command.split("in")[-1].strip()
                return self.get_weather(city)
            else:
                return self.get_weather()
        
        # Web search
        elif "open google" in command or "search google" in command:
            webbrowser.open("https://www.google.com")
            return "Opening Google in your browser."
        
        elif "open youtube" in command:
            webbrowser.open("https://www.youtube.com")
            return "Opening YouTube in your browser."
        
        # Calculator
        elif any(word in command for word in ["calculate", "what is", "plus", "minus", "multiply", "divide"]):
            try:
                # Simple math operations
                command = command.replace("what is", "").replace("calculate", "")
                command = command.replace("plus", "+").replace("add", "+")
                command = command.replace("minus", "-").replace("subtract", "-")
                command = command.replace("multiply", "*").replace("times", "*")
                command = command.replace("divide", "/").replace("divided by", "/")
                
                # Evaluate simple math expressions
                result = eval(command.strip())
                return f"The answer is {result}"
            except:
                return "Sorry, I couldn't calculate that."
        
        # Exit commands
        elif any(word in command for word in ["bye", "goodbye", "exit", "quit"]):
            return "Goodbye! Have a great day!"
        
        else:
            return "I'm not sure how to help with that. You can ask me about time, date, weather, search for information, or do simple calculations."

# Initialize the voice assistant
assistant = VoiceAssistant()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/listen', methods=['POST'])
def listen():
    """Endpoint to capture voice input"""
    try:
        # Listen for voice input
        command = assistant.listen()
        return jsonify({
            'success': True,
            'command': command,
            'message': 'Voice captured successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error capturing voice'
        })

@app.route('/process', methods=['POST'])
def process():
    """Endpoint to process commands and get responses"""
    try:
        data = request.get_json()
        command = data.get('command', '')
        
        # Process the command
        response = assistant.process_command(command)
        
        return jsonify({
            'success': True,
            'response': response,
            'command': command
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error processing command'
        })

@app.route('/speak', methods=['POST'])
def speak():
    """Endpoint to convert text to speech"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if text:
            # Run speech in a separate thread to avoid blocking
            def speak_text():
                assistant.speak(text)
            
            thread = Thread(target=speak_text)
            thread.start()
            
            return jsonify({
                'success': True,
                'message': 'Text spoken successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No text provided'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error speaking text'
        })

if __name__ == '__main__':
    print("Starting Voice Assistant...")
    print("Make sure you have a microphone connected and permissions granted.")
    app.run(debug=True, host='0.0.0.0', port=5000)
