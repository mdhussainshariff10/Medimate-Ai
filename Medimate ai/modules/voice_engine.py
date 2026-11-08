
import speech_recognition as sr
import sounddevice as sd
import numpy as np
import time


class VoiceEngine:

    def __init__(self):
        self.recognizer = sr.Recognizer()

        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.energy_threshold = 300
        self.recognizer.pause_threshold = 1.0
        self.recognizer.non_speaking_duration = 0.6

        self.sample_rate = 16000
        self.record_seconds = 7
        self.block_size = 1024

    def check_microphone(self):
        try:
            devices = sd.query_devices()
            default_input = sd.default.device[0]

            if default_input is None or default_input < 0:
                return False

            return any(
                device.get("max_input_channels", 0) > 0
                for device in devices
            )

        except Exception as error:
            print("Microphone check error:", error)
            return False

    def listen_once(self, audio_level_callback=None):
        try:
            print("\nListening... Speak your complete question.")

            chunks = []
            start_time = time.monotonic()

            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype="float32",
                blocksize=self.block_size
            ) as stream:

                while time.monotonic() - start_time < self.record_seconds:

                    audio_chunk, overflowed = stream.read(self.block_size)

                    audio_chunk = np.squeeze(audio_chunk)
                    chunks.append(audio_chunk.copy())

                    # Calculate actual microphone volume
                    rms = float(
                        np.sqrt(np.mean(np.square(audio_chunk)))
                    )

                    # Normalize volume for waveform display
                    level = min(rms * 8.0, 1.0)

                    if audio_level_callback:
                        audio_level_callback(level)

            audio = np.concatenate(chunks)

            if np.max(np.abs(audio)) < 0.01:
                print("No voice detected.")
                return None

            audio = np.clip(audio, -1.0, 1.0)
            audio = (audio * 32767).astype(np.int16)

            audio_data = sr.AudioData(
                audio.tobytes(),
                self.sample_rate,
                2
            )

            print("Recognizing your speech...")

            command = self.recognizer.recognize_google(
                audio_data,
                language="en-IN"
            )

            command = command.strip().lower()

            if command:
                print("Recognized:", command)
                return command

            return None

        except sr.UnknownValueError:
            print("Speech was not clear. Please try again.")
            return None

        except sr.RequestError as error:
            print("Recognition service error:", error)
            return None

        except Exception as error:
            print("Microphone error:", error)
            return None

        finally:
            if audio_level_callback:
                audio_level_callback(0.0)
