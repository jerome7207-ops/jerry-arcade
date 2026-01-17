#!/usr/bin/env python3
"""
Quick test to verify audio system is working
"""

import sys

print("=" * 50)
print("NO HAND PROGRAMME - SYSTEM TEST")
print("=" * 50)
print()

# Test 1: Check imports
print("Testing required packages...")
errors = []

try:
    import numpy as np
    print("  [OK] numpy")
except ImportError:
    print("  [FAIL] numpy")
    errors.append("numpy")

try:
    import sounddevice as sd
    print("  [OK] sounddevice")
except ImportError:
    print("  [FAIL] sounddevice")
    errors.append("sounddevice")

try:
    import scipy
    print("  [OK] scipy")
except ImportError:
    print("  [FAIL] scipy")
    errors.append("scipy")

try:
    import speech_recognition as sr
    print("  [OK] speech_recognition")
except ImportError:
    print("  [FAIL] speech_recognition")
    errors.append("SpeechRecognition")

try:
    import webrtcvad
    print("  [OK] webrtcvad")
except ImportError:
    print("  [FAIL] webrtcvad")
    errors.append("webrtcvad")

# Optional packages
print("\nOptional packages (for voice training):")
try:
    from resemblyzer import VoiceEncoder
    print("  [OK] resemblyzer")
except ImportError:
    print("  [--] resemblyzer (not installed)")

try:
    import torch
    print("  [OK] torch")
except ImportError:
    print("  [--] torch (not installed)")

if errors:
    print("\n" + "=" * 50)
    print("MISSING PACKAGES - Install with:")
    print(f"  pip install {' '.join(errors)}")
    print("=" * 50)
    sys.exit(1)

# Test 2: Check microphone
print("\n" + "-" * 50)
print("Testing microphone...")

try:
    import sounddevice as sd
    devices = sd.query_devices()
    input_device = sd.query_devices(kind='input')
    print(f"  [OK] Default input: {input_device['name']}")
    print(f"       Sample rate: {int(input_device['default_samplerate'])} Hz")
    print(f"       Channels: {input_device['max_input_channels']}")
except Exception as e:
    print(f"  [FAIL] Microphone error: {e}")
    sys.exit(1)

# Test 3: Quick audio capture test
print("\n" + "-" * 50)
print("Testing audio capture (2 seconds)...")
print("  Speak or make a sound...")

try:
    import numpy as np
    import sounddevice as sd

    duration = 2
    sample_rate = 16000
    audio = sd.rec(int(sample_rate * duration),
                   samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()

    # Check audio level
    peak = np.max(np.abs(audio))
    rms = np.sqrt(np.mean(audio**2))

    print(f"  [OK] Audio captured")
    print(f"       Peak level: {peak:.4f}")
    print(f"       RMS level: {rms:.4f}")

    if peak < 0.01:
        print("  [WARN] Audio level very low - check microphone")
    else:
        print("  [OK] Audio levels look good")

except Exception as e:
    print(f"  [FAIL] Audio capture error: {e}")
    sys.exit(1)

# Summary
print("\n" + "=" * 50)
print("ALL TESTS PASSED")
print("=" * 50)
print("\nYou can now run the main programme:")
print("  python no_hand_programme.py")
print()
print("Commands:")
print("  python no_hand_programme.py train  - Train your voice")
print("  python no_hand_programme.py listen - Continuous listening")
print("  python no_hand_programme.py test   - Single test")
print("=" * 50)
