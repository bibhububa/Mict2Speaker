import pyaudio

# Audio Stream Settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

# Bluetooth Scan Settings
# Duration in seconds for scanning for new devices if needed
SCAN_DURATION: int = 5

# Major Device Content Class for rendering/audio devices
# Used to filter paired devices
BLUETOOTH_MAJOR_AUDIO_DEVICE_CLASS: int = 0x0400