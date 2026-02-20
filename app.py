from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import date
from flask import send_file
from openpyxl import Workbook
from io import BytesIO


app = Flask(__name__)

def get_db():
    return sqlite3.connect("shop.db")

@app.route("/", methods=["GET", "POST"])
def index():
    conn = get_db()
    c = conn.cursor()

    # ===== POST =====
    if request.method == "POST":
        action = request.form.get("action")

        # 1️⃣ THÊM SẢN PHẨM
        if action == "add_product":
            name = request.form["name"]
            stock = int(request.form["stock"])
            import_date = request.form["import_date"]

            c.execute(
                "INSERT INTO products (name, stock, import_date) VALUES (?, ?, ?)",
                (name, stock, import_date)
            )

        # 2️⃣ BÁN HÀNG
        elif action == "sell":
            product_id = int(request.form["product_id"])
            quantity = int(request.form["quantity"])
            sale_date = request.form["sell_date"]

            c.execute("SELECT stock FROM products WHERE id = ?", (product_id,))
            stock = c.fetchone()[0]

            if quantity <= stock:
                c.execute(
                    "INSERT INTO sales (product_id, quantity, sale_date) VALUES (?, ?, ?)",
                    (product_id, quantity, sale_date)
                )
                c.execute(
                    "UPDATE products SET stock = stock - ? WHERE id = ?",
                    (quantity, product_id)
                )

        # 3️⃣ CẬP NHẬT TỒN
        elif action == "update_stock":
            product_id = int(request.form["product_id"])
            new_stock = int(request.form["new_stock"])

            c.execute(
                "UPDATE products SET stock = ? WHERE id = ?",
                (new_stock, product_id)
            )

        # 4️⃣ XÓA SẢN PHẨM
        elif action == "delete_product":
            product_id = int(request.form["product_id"])

            c.execute("DELETE FROM sales WHERE product_id = ?", (product_id,))
            c.execute("DELETE FROM products WHERE id = ?", (product_id,))

        conn.commit()
        conn.close()
        return redirect("/")

    # ===== GET =====
    c.execute("SELECT id, name, stock, import_date FROM products")
    products = c.fetchall()

    c.execute("""
        SELECT sales.sale_date, products.name, sales.quantity
        FROM sales
        JOIN products ON sales.product_id = products.id
        ORDER BY sales.sale_date DESC
    """)
    sales = c.fetchall()

    conn.close()

    return render_template(
        "index.html",
        products=products,
        sales=sales,
        today=date.today().isoformat()
    )




@app.route("/export")
def export_excel():
    conn = sqlite3.connect("shop.db")
    c = conn.cursor()

    c.execute("""
    SELECT sales.sale_date, products.name, sales.quantity
    FROM sales
    JOIN products ON sales.product_id = products.id
    ORDER BY sales.sale_date DESC
    """)
    data = c.fetchall()
    conn.close()

    wb = Workbook()
    ws = wb.active
    ws.title = "Lich su ban"

    ws.append(["Ngày bán", "Tên sản phẩm", "Số lượng"])

    for row in data:
        ws.append(row)

    stream = BytesIO()
    wb.save(stream)
    stream.seek(0)

    return send_file(
        stream,
        as_attachment=True,
        download_name="lich_su_ban_hang.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
@app.route("/history")
def history():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
    SELECT sales.sale_date, products.name, sales.quantity
    FROM sales
    JOIN products ON sales.product_id = products.id
    ORDER BY sales.sale_date DESC
    """)
    sales = c.fetchall()
    conn.close()

    return render_template("history.html", sales=sales)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)