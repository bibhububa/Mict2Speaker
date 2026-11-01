import sys
import subprocess

try:
    import pyaudio
except ImportError:
    # Attempting to install pyaudio at runtime can fail due to missing build tools or permissions.
    # It is recommended to have dependencies installed beforehand.
    print("pyaudio is not installed. Please install it using 'pip install pyaudio'.")
    sys.exit(1)

from config import FORMAT, CHANNELS, RATE, CHUNK

class MicrophoneStreamer:
    """Handles capturing microphone input and providing it as a stream."""

    def __init__(self) -> None:
        self._pa: pyaudio.PyAudio = pyaudio.PyAudio()
        self._stream: pyaudio.Stream | None = None

    def start_stream(self) -> None:
        """Starts the audio recording stream from the microphone."""
        if self._stream is not None and self._stream.is_active():
            return

        try:
            self._stream = self._pa.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK
            )
        except Exception as e:
            raise RuntimeError(f"Failed to open microphone stream: {e}")

    def read_frame(self) -> bytes:
        """
        Reads a single raw audio chunk from the microphone stream.

        Returns:
            bytes: The raw audio data chunk.
        """
        if self._stream is None or not self._stream.is_active():
            raise RuntimeError("Audio stream is not running. Call start_stream() first.")
        
        try:
            return self._stream.read(CHUNK, exception_on_overflow=False)
        except IOError as e:
            # Handle buffer overflow or other I/O errors gracefully
            return b'\x00' * (CHUNK * CHANNELS * self._pa.get_sample_size(FORMAT))

    def stop_stream(self) -> None:
        """Stops and closes the microphone stream."""
        if self._stream:
            try:
                if self._stream.is_active():
                    self._stream.stop_stream()
                self._stream.close()
            except Exception:
                pass
            finally:
                self._stream = None

    def terminate(self) -> None:
        """Releases PyAudio resources."""
        self.stop_stream()
        self._pa.terminate()

    def __enter__(self) -> 'MicrophoneStreamer':
        self.start_stream()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.terminate()