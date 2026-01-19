#!/usr/bin/env python3

import sys
import os
import signal
import time
import paramiko
from scp import SCPClient
from pymobiledevice3.usbmux import select_devices_by_connection_type, create_mux

def get_device():
    """iOS 기기 찾기"""
    devices = select_devices_by_connection_type(connection_type='USB')
    if not devices:
        print("[✗] No iOS device found")
        sys.exit(1)
    
    device = devices[0]
    print(f"[✓] Found device: {device.serial}")
    return device

def transfer_file(device, local_path, remote_path):
    """파일을 iOS 기기로 전송"""
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

def execute_command(transport, command, wait_time=1):
    """SSH 명령 실행"""
    channel = transport.open_session()
    channel.exec_command(command)
    
    # 출력 대기
    time.sleep(wait_time)
    
    output = ""
    if channel.recv_ready():
        output = channel.recv(65535).decode()
    
    error = ""
    if channel.recv_stderr_ready():
        error = channel.recv_stderr(65535).decode()
    
    exit_status = channel.recv_exit_status()
    channel.close()
    
    return exit_status, output, error

def run_bypass(device):
    """바이패스 명령 실행"""
    print("\n[*] Starting activation bypass...")
    print("=" * 50)
    
    mux = create_mux()
    sock = mux.connect(device, 44)
    
    transport = paramiko.Transport(sock)
    transport.connect(username="root", password="alpine")
    
    commands = [
        ("mount -o rw,union,update /", "Remounting filesystem as read-write", 2),
        ("launchctl unload /System/Library/LaunchDaemons/com.apple.mobileactivationd.plist", "Unloading mobileactivationd", 2),
        ("rm /usr/libexec/mobileactivationd", "Removing original mobileactivationd", 1),
        ("uicache --all", "Running uicache (this may take a while)", 30),
        ("cp /var/root/mobileactivationd /usr/libexec/mobileactivationd", "Copying patched mobileactivationd", 2),
        ("chmod 755 /usr/libexec/mobileactivationd", "Setting permissions", 1),
        ("launchctl load /System/Library/LaunchDaemons/com.apple.mobileactivationd.plist", "Loading patched mobileactivationd", 2),
    ]
    
    try:
        for cmd, description, wait_time in commands:
            print(f"\n[*] {description}...")
            print(f"    $ {cmd}")
            
            status, output, error = execute_command(transport, cmd, wait_time)
            
            if output:
                print(f"    {output.strip()}")
            if error:
                print(f"    [!] {error.strip()}")
            
            if status == 0:
                print(f"    [✓] Done")
            else:
                print(f"    [!] Exit code: {status}")
        
        print("\n" + "=" * 50)
        print("[✓] Bypass complete!")
        print("\nNEXT STEP:")
        print("  Tap 'Connect to iTunes' on your device to finish activation")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n[✗] Error: {e}")
    finally:
        transport.close()

def main():
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    signal.signal(signal.SIGTERM, lambda s, f: sys.exit(0))
    
    print("=" * 50)
    print("iOS Activation Bypass Tool")
    print("=" * 50)
    
    # 기기 찾기
    device = get_device()
    
    # 파일 전송
    local_file = os.path.join(os.getcwd(), "mobileactivationd")
    remote_file = "/var/root/mobileactivationd"
    
    if not transfer_file(device, local_file, remote_file):
        sys.exit(1)
    
    # 바이패스 실행
    run_bypass(device)

if __name__ == "__main__":
    main()
