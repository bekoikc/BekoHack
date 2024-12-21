import os
import subprocess

# Kullanıcıdan hedef site ve port bilgisi al
site = input("Site adresini girin (örn: example.com): ")
ports = input("Açık portları girin (örn: 80,443,22): ")

# Sonuçları dosyaya kaydetmek için dosya oluştur
output_file = "pentest_raporu.txt"

def write_output(command, description):
    """Komutun çıktısını bir dosyaya yazdırır."""
    with open(output_file, "a") as file:
        file.write(f"\n### {description} ###\n")
        file.write("=" * 50 + "\n")
        result = subprocess.getoutput(command)
        file.write(result + "\n")

# Temel Testler
write_output(f"nmap -Pn -p {ports} -sV {site}", "Nmap Sonucu (Servis ve Versiyon Tespiti)")
write_output(f"nikto -h {site}", "Nikto Sonucu (Web Sunucu Güvenlik Tarama)")

# SQL Injection Testi (sqlmap)
print("\n### SQL Injection Testi Başlatılıyor ###")
sqlmap_command = f"sqlmap -u 'http://{site}/index.php?id=1' --batch --dbs"
write_output(sqlmap_command, "SQL Injection Testi Sonucu")

# Exploit Tarama (searchsploit)
print("\n### Exploit Kontrolü Başlatılıyor ###")
services = subprocess.getoutput(f"nmap -sV -p {ports} {site}")
with open(output_file, "a") as file:
    file.write("\n### Exploit Araştırması ###\n")
    for line in services.split("\n"):
        if "open" in line:
            service = line.split()[-1]
            searchsploit_command = f"searchsploit {service}"
            exploits = subprocess.getoutput(searchsploit_command)
            file.write(f"\nExploit Araştırması - {service}:\n{exploits}\n")

print("\nTüm testler tamamlandı! Sonuçlar 'pentest_raporu.txt' dosyasına kaydedildi.")
