#!/usr/bin/env python3
import os, json, platform, shutil
import subprocess

# droplets.json dosyasını oku
if not os.path.exists("droplets.json"):
    print("Hata: droplets.json bulunamadı. Önce create_droplets.py çalıştırılmalı.")
    exit(1)

with open("droplets.json") as f:
    data = json.load(f)

droplets = data.get("droplets", [])
password = data.get("password", "")

use_terminal = input("Yeni terminal penceresinde açmak ister misin? (y/n): ").strip().lower() == "y"

def open_ssh_terminal(ip, password):
    ssh_cmd = f"sshpass -p '{password}' ssh -o StrictHostKeyChecking=no root@{ip}"
    system = platform.system().lower()

    if not shutil.which("sshpass"):
        print(f"[!] sshpass yüklü değil. Komut: {ssh_cmd}")
        return

    if not use_terminal:
        os.system(ssh_cmd)
        return

    if system == "darwin":  # macOS
        osascript_cmd = f'''osascript -e 'tell application "Terminal" to do script "{ssh_cmd}"' '''
        os.system(osascript_cmd)
    elif system == "linux":
        if shutil.which("gnome-terminal"):
            os.system(f'gnome-terminal -- bash -c "{ssh_cmd}; exec bash"')
        elif shutil.which("x-terminal-emulator"):
            os.system(f'x-terminal-emulator -e "{ssh_cmd}"')
        else:
            print(f"[!] Uygun terminal bulunamadı. Komut: {ssh_cmd}")
    else:
        print(f"[!] Desteklenmeyen sistem. Komut: {ssh_cmd}")


print("[+] Önce test ekranına geçiliyor...")
script_dir = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(script_dir, "pentest_tool", "main.py")
try:
    subprocess.run(["python3", main_path], check=True)
except Exception as e:
    print(f"[!] main.py başlatılırken hata oluştu: {e}")

print("[+] Testler tamamlandı. Şimdi SSH bağlantıları açılıyor...")

for droplet in droplets:
    name, ip, status = droplet["name"], droplet["ip"], droplet["status"]
    if status == "active" and ip != "-":
        print(f" {name} → SSH root@{ip}")
        open_ssh_terminal(ip, password)
    else:
        print(f" {name} atlanıyor (status={status})")
