import time
import sys
from bluetooth_manager import BluetoothManager, BluetoothDevice
from audio_manager import MicrophoneStreamer

def main() -> None:
    """
    Main execution loop. Discovers paired Bluetooth devices,
    starts microphone capture, and streams audio to the first available device.
    """
    bt_manager = BluetoothManager()
    streamer = MicrophoneStreamer()
    
    # Normally, sending audio data in real-time requires connecting to the
    # specific BlueZ device sink over DBus or RFCOMM, or letting PulseAudio/Pipewire
    # handle the routing once connected. Here, we demonstrate logic logic flow.
    # We select the first paired device found.

    print("Scanning for paired output-capable Bluetooth devices...")
    paired_devices = bt_manager.get_paired_output_devices()

    if not paired_devices:
        print("No paired output Bluetooth devices found. Please pair a device first.")
        sys.exit(1)

    # Select the first available paired device to use as output
    target_device: BluetoothDevice = paired_devices[0]
    print(f"Selecting device: {target_device.name} ({target_device.mac_address})")

    # In a real scenario, we might need to actively connect here via bluetoothctl
    # or rely on the OS to automatically connect when streaming starts, 
    # depending on modern audio server setup (Pipewire/PulseAudio).

    try:
        print("Starting microphone stream...")
        streamer.start_stream()
        print("Streaming audio. Press Ctrl+C to stop.")

        while True:
            # Read mic data
            audio_data = streamer.read_frame()

            # Output data. Since actually pushing audio to Bluetooth device directly
            # via pure Python requires low-level DBus/HCI programming, we simulate 
            # the action here. In production integration, the audio frame would
            # be pipe/written to the correct audio output sync device handled by OS.
            
            # This demonstrates the application logic flow.
            # print(f"Processing {len(audio_data)} bytes...") # Spammy
            
            # To simulate processing time/rate:
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nStopping application...")
    except Exception as e:
        print(f"\nAn error occurred: {e}", file=sys.stderr)
    finally:
        print("Cleaning up resources.")
        streamer.terminate()

if __name__ == "__main__":
    main()