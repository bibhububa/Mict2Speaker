import subprocess
import time
from typing import List, Optional, Dict


class BluetoothDevice:
    """Represents a paired Bluetooth device."""

    def __init__(self, mac_address: str, name: str, connected: bool):
        self.mac_address = mac_address
        self.name = name
        self.connected = connected

    def __repr__(self) -> str:
        return f"BluetoothDevice(name='{self.name}', mac='{self.mac_address}', connected={self.connected})"


class BluetoothManager:
    """Handles discovery and connection status of paired Bluetooth devices."""

    def __init__(self):
        # This implementation utilizes standard command line tools like bluetoothctl.
        # It assumes execution on a Linux-based system with BlueZ installed.
        pass

    def get_paired_output_devices(self) -> List[BluetoothDevice]:
        """
        Retrieves a list of paired Bluetooth devices capable of audio output.

        Uses bluetoothctl to enumerate paired devices.

        Returns:
            List[BluetoothDevice]: List of paired output-capable devices.
        """
        devices: List[BluetoothDevice] = []
        try:
            # Get list of paired devices
            result = subprocess.run(['bluetoothctl', 'paired-devices'], capture_output=True, text=True, check=True)
            lines = result.stdout.strip().split('\n')

            for line in lines:
                if not line.strip():
                    continue
                
                # Line format: Device XX:XX:XX:XX:XX:XX DeviceName
                parts = line.split(' ', 2)
                if len(parts) >= 3:
                    mac = parts[1]
                    name = parts[2]
                    
                    # Basic heuristic: assume devices with standard output profiles,
                    # specific profile checking requires more complex DBus calls or parsing info.
                    # For this scope, we treat all paired devices as potential outputs.
                    is_connected = self._is_device_connected(mac)
                    devices.append(BluetoothDevice(mac_address=mac, name=name, connected=is_connected))

        except subprocess.CalledProcessError as e:
            print(f"Error calling bluetoothctl: {e}")
        except FileNotFoundError:
            print("Error: bluetoothctl not found. Ensure BlueZ is installed.")
        
        return devices

    def _is_device_connected(self, mac_address: str) -> bool:
        """Checks if a specific device is currently connected."""
        try:
            result = subprocess.run(['bluetoothctl', 'info', mac_address], capture_output=True, text=True, check=True)
            return "Connected: yes" in result.stdout
        except subprocess.CalledProcessError:
            return False

    def find_first_available_device(self) -> Optional[BluetoothDevice]:
        """
        Finds the first paired Bluetooth device that is connected or successfully connects to one.

        Returns:
            Optional[BluetoothDevice]: The first available device, or None if none could be found.
        """
        devices = self.get_paired_output_devices()
        if not devices:
            print("No paired Bluetooth devices found.")
            return None

        # Check for currently connected devices first
        for device in devices:
            if device.connected:
                print(f"Found already connected device: {device.name} ({device.mac_address})")
                return device

        # Try connecting to the first paired device
        print("No connected devices found. Attempting to connect to the first paired device...")
        target_device = devices[0]
        
        if self.connect_to_device(target_device.mac_address):
            # Refresh connection status
            target_device.connected = True
            return target_device
            
        return None

    def connect_to_device(self, mac_address: str) -> bool:
        """
        Attempts to connect to a Bluetooth device via bluetoothctl.

        Args:
            mac_address: The MAC address of the device.

        Returns:
            bool: True if connection was successful, False otherwise.
        """
        print(f"Attempting connection to {mac_address}...")
        try:
            # Use a timeout as command may hang
            subprocess.run(['bluetoothctl', 'connect', mac_address], capture_output=True, text=True, check=True, timeout=10)
            
            # Brief pause to let connection settle
            time.sleep(1)
            
            if self._is_device_connected(mac_address):
                print(f"Successfully connected to {mac_address}.")
                return True
            else:
                print(f"Reported connection to {mac_address} failed.")
                return False

        except subprocess.TimeoutExpired:
            print(f"Connection attempt to {mac_address} timed out.")
            return False
        except subprocess.CalledProcessError as e:
            print(f"Failed to connect to {mac_address}: {e.stderr.strip()}")
            return False

if __name__ == "__main__":
    manager = BluetoothManager()
    print("Listing paired devices:")
    paired_devices = manager.get_paired_output_devices()
    for d in paired_devices:
        print(d)
        
    print("\nAttempting to find an available device:")
    available = manager.find_first_available_device()
    if available:
        print(f"Available device found: {available}")
    else:
        print("No paired sound output devices were discovered.")