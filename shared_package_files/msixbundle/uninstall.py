import os
import zipfile
import subprocess
import xml.etree.ElementTree as ET

def run_powershell(command):
    process = subprocess.Popen(["powershell", "-Command", command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print(f"[-] Error: {stderr.strip()}")
    return stdout, process.returncode

def get_package_identity_from_bundle(bundle_path):
    try:
        with zipfile.ZipFile(bundle_path, 'r') as bundle:
            manifest_files = [f for f in bundle.namelist() if f.endswith('AppxManifest.xml')]
            if not manifest_files:
                return None
            
            with bundle.open(manifest_files[0]) as manifest_file:
                tree = ET.parse(manifest_file)
                root = tree.getroot()
                
                namespace = ""
                if root.tag.startswith('{'):
                    namespace = root.tag.split('}')[0] + '}'
                
                identity = root.find(f'.//{namespace}Identity')
                if identity is not None:
                    return identity.get('Name')
    except Exception as e:
        print(f"[-] Failed to read manifest from {os.path.basename(bundle_path)}: {e}")
    return None

def main():
    bundle_files = [f for f in os.listdir('.') if f.endswith('.msixbundle')]
    
    if not bundle_files:
        print("[!] No .msixbundle files found in the current directory to target for uninstallation.")
        return

    print(f"[*] Scanning {len(bundle_files)} bundle(s) for uninstallation...")
    for bundle in bundle_files:
        abs_path = os.path.abspath(bundle)
        pkg_name = get_package_identity_from_bundle(abs_path)
        
        if not pkg_name:
            print(f"[-] Could not resolve package identity for {bundle}. Skipping.")
            continue
            
        print(f"\n[-] Removing package name matching: {pkg_name}")
        cmd = f"Get-AppxPackage -Name '{pkg_name}' | Remove-AppxPackage"
        _, code = run_powershell(cmd)
        if code == 0:
            print(f"[+] Successfully uninstalled package: {pkg_name}")
        else:
            print(f"[-] Uninstallation encountered an issue for: {pkg_name}")

if __name__ == "__main__":
    main()
