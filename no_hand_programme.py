#!/usr/bin/env python3
"""
NO HAND PROGRAMME - Voice-Locked Speech Recognition
DEFENSE_KEY_INFINITY_ARCHITECT Implementation

Only processes YOUR voice. Rejects all other audio sources.
"""

import os
import sys
import json
import time
import wave
import tempfile
from pathlib import Path
from datetime import datetime

# Check for required packages
try:
    import numpy as np
    import sounddevice as sd
    from scipy.io import wavfile
    import speech_recognition as sr
except ImportError as e:
    print("=" * 50)
    print("MISSING PACKAGES - Install with:")
    print("  pip install numpy sounddevice scipy SpeechRecognition")
    print("=" * 50)
    sys.exit(1)

# Try to import voice embedding library
try:
    from resemblyzer import VoiceEncoder, preprocess_wav
    VOICE_TRAINING_AVAILABLE = True
except ImportError:
    VOICE_TRAINING_AVAILABLE = False


class VoiceProfile:
    """Stores the user's voice embedding for verification"""

    PROFILE_DIR = Path.home() / ".no_hand_programme"
    EMBEDDING_FILE = PROFILE_DIR / "voice_embedding.npy"

    def __init__(self):
        self.embedding = None
        self.threshold = 0.75
        self.trained = False
        self.load()

    def load(self):
        if self.EMBEDDING_FILE.exists():
            self.embedding = np.load(self.EMBEDDING_FILE)
            self.trained = True
            return True
        return False

    def save(self, embedding):
        self.PROFILE_DIR.mkdir(parents=True, exist_ok=True)
        np.save(self.EMBEDDING_FILE, embedding)
        self.embedding = embedding
        self.trained = True

    def verify(self, test_embedding):
        if self.embedding is None:
            return False, 0.0
        similarity = np.dot(self.embedding, test_embedding) / (
            np.linalg.norm(self.embedding) * np.linalg.norm(test_embedding)
        )
        return similarity >= self.threshold, float(similarity)


class NoHandProgramme:
    """Voice-locked speech recognition system"""

    def __init__(self):
        self.profile = VoiceProfile()
        self.recognizer = sr.Recognizer()
        self.sample_rate = 16000
        self.encoder = None

        if VOICE_TRAINING_AVAILABLE:
            print("Loading voice encoder...")
            self.encoder = VoiceEncoder()
            print("Ready!")

    def record_audio(self, duration):
        """Record audio from microphone"""
        print(f"\nRecording for {duration} seconds...")

        audio = sd.rec(int(self.sample_rate * duration),
                      samplerate=self.sample_rate,
                      channels=1, dtype='float32')

        for i in range(duration, 0, -1):
            print(f"  {i}...", end=" ", flush=True)
            time.sleep(1)

        sd.wait()
        print("Done!")
        return audio.flatten()

    def has_speech(self, audio):
        """Simple energy-based speech detection"""
        energy = np.sqrt(np.mean(audio**2))
        return energy > 0.01

    def train_voice(self):
        """Train the system to recognize YOUR voice"""
        if not VOICE_TRAINING_AVAILABLE:
            print("\nVoice training requires:")
            print("  pip install resemblyzer torch")
            return False

        print("\n" + "=" * 50)
        print("VOICE TRAINING")
        print("=" * 50)
        print("\nThis trains the system to recognize YOUR voice only.")
        print("After training, other voices will be REJECTED.\n")

        input("Press ENTER when ready...")

        embeddings = []
        prompts = [
            "Say: 'Hello, this is my voice'",
            "Say: 'The quick brown fox jumps over the lazy dog'",
            "Say: 'Testing one two three'",
        ]

        for i, prompt in enumerate(prompts, 1):
            print(f"\nSample {i}/{len(prompts)}: {prompt}")
            input("Press ENTER to record...")

            audio = self.record_audio(4)

            try:
                wav = preprocess_wav(audio, self.sample_rate)
                embedding = self.encoder.embed_utterance(wav)
                embeddings.append(embedding)
                print("Got it!")
            except Exception as e:
                print(f"Error: {e}")

        if len(embeddings) >= 2:
            final = np.mean(embeddings, axis=0)
            self.profile.save(final)
            print("\n" + "=" * 50)
            print("TRAINING COMPLETE - Your voice is now registered")
            print("=" * 50)
            return True
        else:
            print("Not enough samples. Try again.")
            return False

    def verify_speaker(self, audio):
        """Check if audio matches trained voice"""
        if not self.profile.trained or not VOICE_TRAINING_AVAILABLE:
            return True, 1.0

        try:
            wav = preprocess_wav(audio, self.sample_rate)
            embedding = self.encoder.embed_utterance(wav)
            return self.profile.verify(embedding)
        except:
            return False, 0.0

    def recognize_speech(self, audio):
        """Convert audio to text"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            temp_path = f.name

        try:
            audio_int = (audio * 32767).astype(np.int16)
            wavfile.write(temp_path, self.sample_rate, audio_int)

            with sr.AudioFile(temp_path) as source:
                audio_data = self.recognizer.record(source)
                return self.recognizer.recognize_google(audio_data)
        except sr.UnknownValueError:
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None
        finally:
            os.unlink(temp_path)

    def listen_once(self):
        """Listen for a single command"""
        audio = self.record_audio(4)

        if not self.has_speech(audio):
            print("No speech detected.")
            return None

        is_verified, similarity = self.verify_speaker(audio)

        if not is_verified:
            print(f"REJECTED - Voice not recognized ({similarity:.0%} match)")
            return None

        if self.profile.trained:
            print(f"Voice verified ({similarity:.0%} match)")

        text = self.recognize_speech(audio)
        if text:
            print(f'\nYou said: "{text}"')
        return text

    def run(self):
        """Main loop"""
        print("\n" + "=" * 50)
        print("NO HAND PROGRAMME")
        print("DEFENSE_KEY_INFINITY_ARCHITECT")
        print("=" * 50)
        print(f"Voice trained: {self.profile.trained}")
        if not VOICE_TRAINING_AVAILABLE:
            print("(Install resemblyzer + torch for voice lock)")
        print("=" * 50)

        while True:
            print("\n1. Train voice")
            print("2. Test recognition")
            print("3. Continuous listen")
            print("4. Exit")

            choice = input("\nChoice: ").strip()

            if choice == "1":
                self.train_voice()
            elif choice == "2":
                self.listen_once()
            elif choice == "3":
                print("\nListening... (Ctrl+C to stop)")
                try:
                    while True:
                        self.listen_once()
                        time.sleep(0.5)
                except KeyboardInterrupt:
                    print("\nStopped.")
            elif choice == "4":
                break


if __name__ == "__main__":
    prog = NoHandProgramme()
    prog.run()
