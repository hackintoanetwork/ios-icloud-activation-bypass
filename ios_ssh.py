#!/usr/bin/env python3

import os
import sys
import tty
import signal
import select
import termios
import argparse
import paramiko
from scp import SCPClient
from pymobiledevice3.usbmux import select_devices_by_connection_type, create_mux

def get_device():
    devices = select_devices_by_connection_type(connection_type='USB')
    if not devices:
        print("[✗] No iOS device found")
        sys.exit(1)
    device = devices[0]
    print(f"[✓] Found device: {device.serial}")
    return device

def transfer_file(device, local_path, remote_path):
    if not os.path.exists(local_path):
        print(f"[✗] File not found: {local_path}")
        return False
    
    print(f"[*] Transferring {local_path} to {remote_path}...")
    
    mux = create_mux()
    sock = mux.connect(device, 44)
    
    transport = paramiko.Transport(sock)
    transport.connect(username="root", password="alpine")
    
    try:
        with SCPClient(transport) as scp:
            scp.put(local_path, remote_path)
        print(f"[✓] Transfer complete!")
        return True
    except Exception as e:
        print(f"[✗] Transfer failed: {e}")
        return False
    finally:
        transport.close()

def interactive_shell(device):
    mux = create_mux()
    sock = mux.connect(device, 44)
    
    transport = paramiko.Transport(sock)
    transport.connect(username="root", password="alpine")
    
    channel = transport.open_session()
    channel.get_pty()
    channel.invoke_shell()
    
    oldtty = termios.tcgetattr(sys.stdin)
    try:
        tty.setraw(sys.stdin.fileno())
        channel.settimeout(0.0)
        
        while True:
            r, w, e = select.select([channel, sys.stdin], [], [])
            if channel in r:
                try:
                    data = channel.recv(1024)
                    if not data:
                        break
                    sys.stdout.write(data.decode())
                    sys.stdout.flush()
                except:
                    break
            if sys.stdin in r:
                data = sys.stdin.read(1)
                if not data:
                    break
                channel.send(data)
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)
    
    channel.close()
    transport.close()

def main():
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    signal.signal(signal.SIGTERM, lambda s, f: sys.exit(0))
    
    parser = argparse.ArgumentParser(description='iOS SSH Tool')
    parser.add_argument('-t', '--transfer', nargs=2, metavar=('LOCAL', 'REMOTE'),
                        help='Transfer file: -t <local_path> <remote_path>')
    parser.add_argument('-s', '--shell', action='store_true',
                        help='Start interactive shell')
    
    args = parser.parse_args()
    
    device = get_device()
    
    if args.transfer:
        local_path, remote_path = args.transfer
        transfer_file(device, local_path, remote_path)
    else:
        print("\n[*] Starting interactive shell...\n")
        interactive_shell(device)

if __name__ == "__main__":
    main()