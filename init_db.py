import sqlite3

conn = sqlite3.connect("shop.db")
c = conn.cursor()

# Bảng sản phẩm (hàng tồn)
c.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    stock INTEGER
)
""")

# Bảng bán theo ngày
c.execute("""
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    quantity INTEGER,
    sale_date TEXT
)
""")

# Sản phẩm mẫu (em có thể đổi tên + số lượng)
products = [
    ("Thau", 20),
    ("Bàn", 15),
    ("Nồi", 10)
]

c.executemany(
    "INSERT INTO products (name, stock) VALUES (?, ?)",
    products
)

conn.commit()
conn.close()

print("Đã tạo xong database & sản phẩm")
