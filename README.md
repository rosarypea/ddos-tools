# Cyberwhiz DDoS Tools  

Bu proje, **DigitalOcean üzerinde droplet oluşturma**, **otomatik bağlantı sağlama** ve **L3/L7 DDoS testleri** yapmayı kolaylaştırmak için geliştirilmiş bir araç setidir.  
Tamamen **eğitim ve sızma testi (pentest) senaryoları** için tasarlanmıştır.  

---

## Dosya Açıklamaları  

- **`crate_droplet.py`**  
  DigitalOcean API üzerinden yeni droplet oluşturur. Oluşturulan droplet bilgileri **`run.json`** dosyasına kaydedilir.  

- **`connect_droplets.py`**  
  `run.json` içindeki bilgilerle droplet’lere bağlanır. Bağlantı sonrası `pentest_tool/main.py` çalıştırılarak testler tetiklenir.  

- **`pentest_tool/main.py`**  
  Projenin ana çalışma dosyasıdır. Kullanıcıya hangi testlerin yapılacağını sorar ve ilgili modülü (`l3_tests.py` veya `l7_tests.py`) çağırır.  

- **`pentest_tool/l3_tests.py`**  
  Layer 3 testlerini (UDP flood, TCP flood vb.) gerçekleştirir.  

- **`pentest_tool/l7_tests.py`**  
  Layer 7 testlerini (HTTP flood, Slowloris, POST/GET flood vb.) gerçekleştirir.  

- **`pentest_tool/report.py`**  
  Çalıştırılan testlerin raporlarını oluşturur. JSON veya HTML formatında kaydedebilir.  

- **`pentest_tool/utils.py`**  
  Ortak fonksiyonları (dosya okuma, validasyon, hata yakalama) barındırır.  

- **`run.json`**  
  Tüm droplet bilgileri (ID, IP adresi, oluşturulma tarihi) burada saklanır. Hem bağlantı hem raporlama aşamasında kullanılır.  

---

## Ön Hazırlık / Kurulum

Bu projeyi çalıştırmadan önce aşağıdaki adımları tamamlamanız gerekir:  

### 1. Gerekli Linux Tool’ları Kurun  
Testlerin sorunsuz çalışması için aşağıdaki araçların sisteminizde kurulu olması gerekir:  

```
sudo apt-get update -y
sudo apt-get install -y sshpass curl hping3 vegeta unzip python3 python3-pip
```
---
  
### 2. Repoyu Klonlayın

Github reposunu sisteminize indirin:

```
git clone https://github.com/senaykt/cyberwhiz-ddos-tools.git
cd cyberwhiz-ddos-tools
```
---

### 3. Python Bağımlılıklarını Kurun

Proje için gerekli Python kütüphanelerini kurun:

```
pip install -r requirements.txt
```

Eğer requirements.txt yoksa elle şu kütüphaneleri yükleyin:

```
pip install requests paramiko python-dotenv jinja2
```
--- 

### 4. DigitalOcean API Token Ayarlayın

Droplet oluşturma işlemleri için DigitalOcean’dan aldığınız API token’ı ortam değişkenine ekleyin:

```
export DO_API_TOKEN="your_digitalocean_token"
```

Token’ın tanımlı olup olmadığını doğrulamak için:

```
echo $DO_API_TOKEN
```
---

### 5. İlk Çalıştırma (Test)

Her şeyin doğru kurulduğunu görmek için örnek olarak droplet oluşturma scriptini çalıştırın:

```
python3 crate_droplet.py
```

Oluşturulan bilgiler `run.json` dosyasına kaydedilmiş olmalı.

---

## Çalıştırma 

### 1. Droplet Oluşturma  

Önce DigitalOcean üzerinde test için kullanacağınız droplet’leri oluşturun:  

```
python3 crate_droplet.py
```

Oluşturulan droplet bilgileri (ID, IP, kullanıcı adı, şifre) `run.json` dosyasına kaydedilir.

Eğer `run.json` yoksa testler çalışmaz.

---

### 2. Droplet’lere Bağlanma
Droplet’ler hazır olduğunda bağlantıyı sağlamak için: (yalnız bu noktada 15 dakika sonra kodun koşturulması lazım diğer türlü bağlantı sağlanamaz)

```
python3 connect_droplets.py
```

Script, `run.json` dosyasındaki bilgileri okuyarak otomatik SSH bağlantısı kurar.

Bağlantı öncesinde `pentest_tool/main.py` çalıştırılır. Akabinde SSH bağlantısı karşımıza gelir.

---

### 3. Testleri Başlatma

Droplet’lere bağlandıktan sonra ana menü açılır. Buradan hangi testin çalıştırılacağını seçebilirsiniz:

```
python3 pentest_tool/main.py
```

- L3 Testleri → l3_tests.py (UDP flood, TCP flood)
- L7 Testleri → l7_tests.py (HTTP flood, Slowloris, POST/GET flood)
- Kullanıcıdan alınan yanıtlara göre uygun testler çalıştırılır.

---

### 4. Raporlama

- Testler tamamlandıktan sonra raporlar otomatik oluşturulur.
- `report.py` raporları işler.
- Varsayılan kayıt yeri: çalışma dizini.
- JSON ve HTML formatında rapor alınabilir.

Örnek rapor:

```
python3 pentest_tool/report.py
```

Tüm sonuçlar ayrıca `run.json` dosyasında da saklanır.

---

## Notlar & Uyarılar

- Bu proje yalnızca **eğitim amaçlı** ve **izinli sızma testleri** için geliştirilmiştir.  
  İzinsiz kullanımlar **yasal sorumluluk** doğurur. ( :) )  

-  **`run.json`** dosyası, droplet bilgilerini saklar. Bu dosya silinirse  
  bağlantılar ve raporlar çalışmaz.  

-  `connect_droplets.py` çalıştırmadan önce droplet’lerin **10–15 dakika içinde**  
  şifreyle girişe hazır hale gelmesini bekleyin.  

-  DigitalOcean üzerinde oluşturduğunuz droplet’ler ücretlidir. Testlerden sonra  
  ekstra maliyet çıkmaması için droplet’leri silmeyi unutmayın.  

-  API token’ın gizliliğine dikkat edin. Token sızarsa hesabınız tehlikeye girer.  
