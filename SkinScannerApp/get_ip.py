"""
Quick script to get your desktop's local IP address for phone connection.
Run: python get_ip.py
"""
import socket

def get_local_ip():
    """Get the local IP address of this machine."""
    try:
        # Create a socket and connect to an external address
        # This doesn't actually send data, just determines the local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "Unable to determine IP"

if __name__ == "__main__":
    ip = get_local_ip()
    print("\n" + "="*60)
    print("🌐 YOUR DESKTOP'S LOCAL IP ADDRESS")
    print("="*60)
    print(f"\nIP Address: {ip}")
    print(f"\n📱 On your phone, open your browser and go to:")
    print(f"   https://{ip}:5173")
    print(f"\n⚠️  Important:")
    print(f"   1. You MUST use HTTPS (not HTTP) for camera to work!")
    print(f"   2. Your browser will show a security warning - click")
    print(f"      'Advanced' and 'Proceed anyway' (certificate is self-signed)")
    print("\n" + "="*60)
    print("\n📝 Make sure:")
    print("  1. Your phone and desktop are on the same WiFi network")
    print("  2. Your firewall allows connections on ports 5173 and 8000")
    print("  3. Accept the security warning on your phone")
    print("="*60 + "\n")
