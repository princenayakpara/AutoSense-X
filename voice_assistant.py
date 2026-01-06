"""
Voice Assistant Module - "Hey AutoSense boost system"
"""
import speech_recognition as sr
import pyttsx3
import threading
import queue
from ai_engine import AISystemBrain

class VoiceAssistant:
    """Voice assistant for AutoSense X"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.engine = pyttsx3.init()
        self.ai_engine = AISystemBrain()
        self.is_listening = False
        self.command_queue = queue.Queue()
        
        # Configure TTS
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 0.8)
    
    def speak(self, text: str):
        """Speak text using TTS"""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"TTS Error: {e}")
    
    def listen_for_wake_word(self):
        """Listen for 'Hey AutoSense' wake word"""
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
        
        while self.is_listening:
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
                
                try:
                    text = self.recognizer.recognize_google(audio).lower()
                    if "hey autosense" in text or "autosense" in text:
                        self.speak("Yes, how can I help you?")
                        self.listen_for_command()
                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    print(f"Recognition error: {e}")
            except sr.WaitTimeoutError:
                pass
            except Exception as e:
                print(f"Listening error: {e}")
    
    def listen_for_command(self):
        """Listen for command after wake word"""
        try:
            with self.microphone as source:
                self.speak("Listening for command...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
            
            try:
                command = self.recognizer.recognize_google(audio).lower()
                self.process_command(command)
            except sr.UnknownValueError:
                self.speak("I didn't catch that. Please try again.")
            except sr.RequestError as e:
                self.speak("Sorry, I'm having trouble understanding.")
        except sr.WaitTimeoutError:
            self.speak("No command detected.")
        except Exception as e:
            print(f"Command listening error: {e}")
    
    def process_command(self, command: str):
        """Process voice command"""
        command = command.lower()
        
        if "boost" in command or "optimize" in command:
            if "ram" in command or "memory" in command:
                self.speak("Boosting RAM now...")
                result = self.ai_engine._optimize_ram()
                if result.get("success"):
                    self.speak(f"RAM boost complete. Freed {result.get('freed_percent', 0):.1f} percent memory.")
                else:
                    self.speak("RAM boost failed. Please try again.")
            elif "system" in command or "cpu" in command:
                self.speak("Optimizing system now...")
                result = self.ai_engine.auto_optimize()
                if result.get("success"):
                    self.speak("System optimization complete.")
                else:
                    self.speak("Optimization failed. Please try again.")
            else:
                self.speak("Optimizing system...")
                result = self.ai_engine.auto_optimize()
                if result.get("success"):
                    self.speak("System optimized successfully.")
        
        elif "clean" in command or "junk" in command:
            self.speak("Cleaning junk files...")
            # This would call the junk file cleaner
            self.speak("Junk file cleanup initiated.")
        
        elif "status" in command or "health" in command:
            self.speak("Checking system health...")
            prediction = self.ai_engine.predict_degradation_risk()
            risk_level = prediction.get("risk_level", "unknown")
            self.speak(f"System health is {risk_level}. {prediction.get('explanation', '')}")
        
        elif "report" in command:
            self.speak("Generating system report...")
            # This would trigger PDF generation
            self.speak("Report generation initiated.")
        
        else:
            self.speak("I didn't understand that command. You can ask me to boost RAM, optimize system, clean junk files, check status, or generate a report.")
    
    def start(self):
        """Start voice assistant"""
        self.is_listening = True
        self.speak("AutoSense voice assistant activated. Say 'Hey AutoSense' to begin.")
        thread = threading.Thread(target=self.listen_for_wake_word, daemon=True)
        thread.start()
    
    def stop(self):
        """Stop voice assistant"""
        self.is_listening = False
        self.speak("Voice assistant deactivated.")


def activate_voice_assistant():
    """Activate voice assistant"""
    assistant = VoiceAssistant()
    assistant.start()
    return assistant

