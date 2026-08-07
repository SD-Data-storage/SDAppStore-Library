import os
import subprocess

def run_powershell(command):
    process = subprocess.Popen(["powershell", "-Command", command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print(f"[-] Error: {stderr.strip()}")
    return stdout, process.returncode

def main():
    bundle_files = [f for f in os.listdir('.') if f.endswith('.msixbundle')]
    
    if not bundle_files:
        print("[!] No .msixbundle files found in the current directory.")
        return

    print(f"[*] Found {len(bundle_files)} bundle(s) to install.")
    for bundle in bundle_files:
        abs_path = os.path.abspath(bundle)
        print(f"\n[+] Installing: {bundle}")
        cmd = f"Add-AppxPackage -Path '{abs_path}'"
        _, code = run_powershell(cmd)
        if code == 0:
            print(f"[+] Successfully installed: {bundle}")
        else:
            print(f"[-] Installation failed for: {bundle}")

if __name__ == "__main__":
    main()
