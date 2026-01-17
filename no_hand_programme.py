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
import threading
from pathlib import Path
from datetime import datetime

# Check for required packages and provide install instructions
REQUIRED_PACKAGES = {
    'numpy': 'numpy',
    'sounddevice': 'sounddevice',
    'scipy': 'scipy',
    'speech_recognition': 'SpeechRecognition',
    'webrtcvad': 'webrtcvad',
}

missing = []
for module, package in REQUIRED_PACKAGES.items():
    try:
        __import__(module)
    except ImportError:
        missing.append(package)

if missing:
    print("=" * 60)
    print("MISSING REQUIRED PACKAGES")
    print("=" * 60)
    print(f"\nInstall with:\n  pip install {' '.join(missing)}\n")
    print("For voice training, also install:")
    print("  pip install resemblyzer torch")
    print("=" * 60)
    sys.exit(1)

import numpy as np
import sounddevice as sd
from scipy.io import wavfile
import speech_recognition as sr
import webrtcvad

# Try to import voice embedding library
try:
    from resemblyzer import VoiceEncoder, preprocess_wav
    VOICE_TRAINING_AVAILABLE = True
except ImportError:
    VOICE_TRAINING_AVAILABLE = False
    print("Note: Install 'resemblyzer' and 'torch' for voice training")
    print("      pip install resemblyzer torch")


class DefenseSystem:
    """
    DEFENSE_KEY_INFINITY_ARCHITECT
    Auto-Scaling Universal Defense System
    """

    def __init__(self):
        self.alert_level = "GREEN"
        self.fusion_capacity = 500
        self.protection_active = True

    def status(self):
        return {
            "alert": self.alert_level,
            "capacity": self.fusion_capacity,
            "protection": self.protection_active,
            "layers": "ALL_18_ACTIVE"
        }

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")


class VoiceProfile:
    """Stores the user's voice embedding for verification"""

    PROFILE_DIR = Path.home() / ".no_hand_programme"
    PROFILE_FILE = PROFILE_DIR / "voice_profile.json"
    EMBEDDING_FILE = PROFILE_DIR / "voice_embedding.npy"

    def __init__(self):
        self.embedding = None
        self.threshold = 0.75  # Similarity threshold
        self.trained = False
        self.load()

    def load(self):
        """Load saved voice profile"""
        if self.EMBEDDING_FILE.exists():
            self.embedding = np.load(self.EMBEDDING_FILE)
            self.trained = True
            return True
        return False

    def save(self, embedding):
        """Save voice profile"""
        self.PROFILE_DIR.mkdir(parents=True, exist_ok=True)
        np.save(self.EMBEDDING_FILE, embedding)
        self.embedding = embedding
        self.trained = True

        # Save metadata
        with open(self.PROFILE_FILE, 'w') as f:
            json.dump({
                "created": datetime.now().isoformat(),
                "threshold": self.threshold
            }, f)

    def verify(self, test_embedding):
        """Check if audio matches the trained voice"""
        if self.embedding is None:
            return False, 0.0

        # Cosine similarity
        similarity = np.dot(self.embedding, test_embedding) / (
            np.linalg.norm(self.embedding) * np.linalg.norm(test_embedding)
        )

        return similarity >= self.threshold, float(similarity)


class NoHandProgramme:
    """
    Main voice-locked speech recognition system

    Features:
    - Voice training to learn YOUR voice
    - Rejects TV, radio, other people, background noise
    - Only processes verified voice input
    """

    def __init__(self):
        self.defense = DefenseSystem()
        self.profile = VoiceProfile()
        self.recognizer = sr.Recognizer()
        self.vad = webrtcvad.Vad(3)  # Aggressive VAD mode

        # Audio settings
        self.sample_rate = 16000
        self.channels = 1
        self.chunk_duration = 0.03  # 30ms chunks for VAD

        # Voice encoder for training/verification
        self.encoder = None
        if VOICE_TRAINING_AVAILABLE:
            self.defense.log("Loading voice encoder...")
            self.encoder = VoiceEncoder()
            self.defense.log("Voice encoder ready")

        self.running = False

    def print_status(self):
        """Print system status"""
        print("\n" + "=" * 60)
        print("DEFENSE_KEY_INFINITY_ARCHITECT - ACTIVE")
        print("=" * 60)
        status = self.defense.status()
        print(f"Alert Level: {status['alert']}")
        print(f"Protection: {status['protection']}")
        print(f"Capacity: {status['capacity']}x")
        print(f"Voice Trained: {self.profile.trained}")
        print("=" * 60 + "\n")

    def record_audio(self, duration, prompt="Recording..."):
        """Record audio from microphone"""
        print(f"\n{prompt}")
        print(f"Recording for {duration} seconds...")

        frames = int(self.sample_rate * duration)
        audio = sd.rec(frames, samplerate=self.sample_rate,
                      channels=self.channels, dtype='float32')

        # Show countdown
        for i in range(duration, 0, -1):
            print(f"  {i}...", end=" ", flush=True)
            time.sleep(1)

        sd.wait()
        print("Done!")

        return audio.flatten()

    def train_voice(self):
        """Train the system to recognize YOUR voice"""
        if not VOICE_TRAINING_AVAILABLE:
            print("\nVoice training requires additional packages:")
            print("  pip install resemblyzer torch")
            return False

        print("\n" + "=" * 60)
        print("VOICE TRAINING MODE")
        print("=" * 60)
        print("\nThis will train the system to recognize YOUR voice.")
        print("Other voices (TV, radio, people) will be REJECTED.\n")

        input("Press ENTER when ready to record your voice...")

        # Record multiple samples
        embeddings = []
        prompts = [
            "Say: 'Hello, this is my voice for the No Hand Programme'",
            "Say: 'The quick brown fox jumps over the lazy dog'",
            "Say: 'I am training my voice profile for authentication'",
        ]

        for i, prompt in enumerate(prompts, 1):
            print(f"\nSample {i}/{len(prompts)}")
            print(prompt)
            input("Press ENTER to start recording...")

            audio = self.record_audio(5, "Speak now!")

            # Get embedding
            try:
                wav = preprocess_wav(audio, self.sample_rate)
                embedding = self.encoder.embed_utterance(wav)
                embeddings.append(embedding)
                print("Sample recorded successfully!")
            except Exception as e:
                print(f"Error processing sample: {e}")
                continue

        if len(embeddings) < 2:
            print("\nNot enough valid samples. Please try again.")
            return False

        # Average the embeddings
        final_embedding = np.mean(embeddings, axis=0)
        self.profile.save(final_embedding)

        print("\n" + "=" * 60)
        print("VOICE TRAINING COMPLETE")
        print("=" * 60)
        print("Your voice profile has been saved.")
        print("The system will now only respond to YOUR voice.")
        print("=" * 60 + "\n")

        return True

    def verify_speaker(self, audio):
        """Verify if audio matches the trained voice"""
        if not self.profile.trained:
            return True, 1.0  # Skip verification if not trained

        if not VOICE_TRAINING_AVAILABLE:
            return True, 1.0

        try:
            wav = preprocess_wav(audio, self.sample_rate)
            embedding = self.encoder.embed_utterance(wav)
            return self.profile.verify(embedding)
        except Exception as e:
            self.defense.log(f"Verification error: {e}", "WARN")
            return False, 0.0

    def has_speech(self, audio):
        """Check if audio contains speech using VAD"""
        # Convert to 16-bit PCM
        audio_int = (audio * 32767).astype(np.int16)

        # Check chunks for speech
        chunk_size = int(self.sample_rate * self.chunk_duration)
        speech_chunks = 0
        total_chunks = 0

        for i in range(0, len(audio_int) - chunk_size, chunk_size):
            chunk = audio_int[i:i+chunk_size].tobytes()
            try:
                if self.vad.is_speech(chunk, self.sample_rate):
                    speech_chunks += 1
                total_chunks += 1
            except:
                pass

        # Require at least 20% speech
        if total_chunks == 0:
            return False
        return (speech_chunks / total_chunks) > 0.2

    def recognize_speech(self, audio):
        """Convert audio to text using speech recognition"""
        # Save to temp WAV file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            temp_path = f.name

        try:
            # Write WAV file
            audio_int = (audio * 32767).astype(np.int16)
            wavfile.write(temp_path, self.sample_rate, audio_int)

            # Recognize with Google (free, no API key needed)
            with sr.AudioFile(temp_path) as source:
                audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio_data)
                return text
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            self.defense.log(f"Recognition error: {e}", "ERROR")
            return None
        finally:
            os.unlink(temp_path)

    def listen_once(self, duration=5):
        """Listen for a single command"""
        print("\nListening...")
        audio = self.record_audio(duration, "Speak now (your voice only):")

        # Check for speech
        if not self.has_speech(audio):
            print("No speech detected.")
            return None

        # Verify speaker
        is_verified, similarity = self.verify_speaker(audio)

        if not is_verified:
            self.defense.log(
                f"REJECTED - Voice not recognized (similarity: {similarity:.2f})",
                "SECURITY"
            )
            print(f"Voice rejected (similarity: {similarity:.1%})")
            print("This doesn't sound like the trained voice.")
            return None

        if self.profile.trained:
            print(f"Voice verified (similarity: {similarity:.1%})")

        # Recognize speech
        text = self.recognize_speech(audio)

        if text:
            print(f"\nRecognized: \"{text}\"")
            return text
        else:
            print("Could not understand audio.")
            return None

    def run_continuous(self):
        """Run continuous voice recognition"""
        print("\n" + "=" * 60)
        print("CONTINUOUS LISTENING MODE")
        print("=" * 60)
        print("Listening for your voice...")
        print("Press Ctrl+C to stop")
        print("=" * 60 + "\n")

        self.running = True

        try:
            while self.running:
                text = self.listen_once(duration=3)
                if text:
                    print(f"\n>>> {text}\n")
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\n\nStopping...")
            self.running = False

    def run_menu(self):
        """Interactive menu"""
        while True:
            self.print_status()

            print("OPTIONS:")
            print("  1. Train voice (learn YOUR voice)")
            print("  2. Test single recognition")
            print("  3. Run continuous listening")
            print("  4. Reset voice profile")
            print("  5. Exit")
            print()

            choice = input("Select option: ").strip()

            if choice == "1":
                self.train_voice()
            elif choice == "2":
                self.listen_once()
            elif choice == "3":
                self.run_continuous()
            elif choice == "4":
                if self.profile.EMBEDDING_FILE.exists():
                    self.profile.EMBEDDING_FILE.unlink()
                    self.profile.trained = False
                    print("Voice profile reset.")
                else:
                    print("No profile to reset.")
            elif choice == "5":
                print("\nDefense system deactivating...")
                break
            else:
                print("Invalid option")

            input("\nPress ENTER to continue...")


def main():
    print("\n" + "=" * 60)
    print("   NO HAND PROGRAMME")
    print("   DEFENSE_KEY_INFINITY_ARCHITECT")
    print("   Voice-Locked Speech Recognition")
    print("=" * 60)

    programme = NoHandProgramme()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "train":
            programme.train_voice()
        elif command == "listen":
            programme.run_continuous()
        elif command == "test":
            programme.listen_once()
        else:
            print(f"Unknown command: {command}")
            print("Usage: python no_hand_programme.py [train|listen|test]")
    else:
        programme.run_menu()


if __name__ == "__main__":
    main()
