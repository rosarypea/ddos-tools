#!/usr/bin/env python3
import os, sys, time, json, requests, random

TOKEN = os.environ.get("DO_API_TOKEN","")
if not TOKEN:
    print("Hata: DO_API_TOKEN ortam değişkenini ayarla.")
    sys.exit(1)

H = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
API = "https://api.digitalocean.com/v2"

def to_int(s, d=1):
    try: return int(s)
    except: return d

adet    = to_int(input("Kaç droplet oluşturulsun? (örn 1-20): ").strip(), 1)
prefix  = (input("İsim prefix'i? (boşsa 'web'): ").strip() or "web").lower()
passwd  = input("Root parolası ne olsun? (örn: MySecurePass123): ").strip() or "MySecurePass123"

REGIONS = ["fra1", "ams3", "lon1", "nyc3", "sfo3", "sgp1", "blr1", "tor1"]
SIZE    = "s-1vcpu-1gb"
IMAGE   = "ubuntu-22-04-x64"
SSHKEYS = []
TAGS    = ["env:test", "role:web"]

def choose_region():
    return random.choice(REGIONS)

def create_droplet(name, region, password):
    user_data = (
        "#!/bin/bash\n"
        f"echo root:{password} | chpasswd\n"
        "sed -i 's/^#*PasswordAuthentication .*/PasswordAuthentication yes/' /etc/ssh/sshd_config\n"
        "systemctl restart ssh\n"
        "echo \"Hazır: $(hostname)\" > /root/READY.txt"
    )

    payload = {
        "name": name,
        "region": region,
        "size": SIZE,
        "image": IMAGE,
        "ssh_keys": SSHKEYS,
        "backups": False,
        "ipv6": False,
        "monitoring": True,
        "tags": TAGS,
        "user_data": user_data
    }

    r = requests.post(f"{API}/droplets", headers=H, data=json.dumps(payload), timeout=60)
    if r.status_code not in (200, 202):
        raise RuntimeError(f"Oluşturma hatası {name}@{region}: {r.status_code} {r.text}")
    return r.json()["droplet"]["id"]

def wait_active_get_ip(did, timeout_s=180):
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        rr = requests.get(f"{API}/droplets/{did}", headers=H, timeout=30)
        d = rr.json().get("droplet", {})
        status = d.get("status")
        nets = d.get("networks", {})
        ipv4 = [n["ip_address"] for n in nets.get("v4", []) if n.get("type") == "public"]
        if status == "active" and ipv4:
            return ipv4[0]
        time.sleep(5)
    return None

results = []
print(f"\n→ {adet} adet droplet oluşturuluyor (size={SIZE}, image={IMAGE})...")
for i in range(1, adet+1):
    name = f"{prefix}-{i:02d}"
    region = choose_region()
    try:
        did = create_droplet(name, region, passwd)
        print(f"✓ İstek gönderildi: {name} @ {region} (ID={did})")
        ip = wait_active_get_ip(did)
        if ip:
            print(f"  → Aktif: {name} IP={ip}")
            results.append({"name": name, "region": region, "id": did, "ip": ip, "status": "active"})
        else:
            print(f"  → Uyarı: {name} zaman aşımı; IP alınamadı.")
            results.append({"name": name, "region": region, "id": did, "ip": "-", "status": "timeout"})
    except Exception as e:
        print(f"✗ Hata: {name} @ {region}: {e}")
        results.append({"name": name, "region": region, "id": "-", "ip": "-", "status": "create_error"})

# JSON dosyasına yaz
with open("droplets.json", "w") as f:
    json.dump({"droplets": results, "password": passwd}, f, indent=2)

print("\n Droplet bilgileri droplets.json dosyasına kaydedildi.")
