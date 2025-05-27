# DHT-NETHUNTER

![DHT-TRACKER](https://img.shields.io/badge/DHT-HACKERS-red?style=for-the-badge)

**The most powerful Kali NetHunter installer for Termux. Built with a stunning Rich UI by [TEAM HCO].**

---

## ⚙️ Features

- [x] Rich-powered banner and UI
- [x] Auto-detects device architecture
- [x] Downloads and extracts the official Kali NetHunter RootFS
- [x] Creates easy-to-use `nethunter` and `nh` launchers
- [x] Automatically sets permissions and sudo access
- [x] Fixes UID for non-root Android Termux compatibility

---

## ⚠️ Disclaimer

> This tool is only for **ethical hacking** and **educational** purposes.  
> Any misuse of this tool is **strictly prohibited**.  
> The authors are **not responsible** for any illegal use.

---

## 🚀 Installation

Open **Termux** and run the following:

```python
apt update && apt upgrade -y
pkg install git python proot-distro wget tar -y
pip install pyfiglet rich
git clone https://github.com/DHThackers-10/DHT-NETHUNTER-.git
cd DHT-NETHUNTER- 
python3 DHT-NETHUNTER.py
```
# Kali-menu error solution 
```
mkdir -p /usr/share/kali-menu

echo -e '#!/bin/sh\nexit 0' > /usr/share/kali-menu/update-kali-menu

chmod +x /usr/share/kali-menu/update-kali-menu
```

#Kex error solution 

```
rm -f /usr/bin/perl
find /usr/bin -type f -executable -name 'perl*'
ln -s /usr/bin/perl5.40-aarch64-linux-gnu /usr/bin/perl
perl -v
```
now run 
```
kex
```
---

# ✅ Usage Instructions

After installation, use the following commands inside Termux:

nethunter             # Start Kali CLI
nethunter kex passwd  # Set GUI (KeX) password
nethunter kex &       # Start GUI mode
nethunter kex stop    # Stop GUI
nethunter -r          # Start as root user
nh                    # Shortcut alias


---

# 📷 Interface Preview

> All banners, prompts, and panels are styled with the Rich library for a clean and modern look

![Screenshot_20250522-184613](https://github.com/user-attachments/assets/7309f2ef-da7a-41de-b35e-d66ce87c279f)



---

# 🤖 Requirements

Android with Termux

12GB+ free space

Internet connection

Python 3.x



---

# 👨‍💻 Author & Credits

Tool by: [TEAM HCO]

Channel: [YouTube – DHT Hackers](https://youtube.com/@dht-hackers_10?feature=shared)

GitHub: [follow](https://github.com/DHThackers-10)

WhatsApp Community: [Join Us](https://chat.whatsapp.com/G2hCkCzylra2OENEfhH8Os)

