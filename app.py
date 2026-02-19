from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import date

app = Flask(__name__)

def get_db():
    return sqlite3.connect("shop.db")

@app.route("/", methods=["GET", "POST"])
def index():
    conn = get_db()
    c = conn.cursor()

    if request.method == "POST":
        action = request.form["action"]

        # 1️⃣ THÊM SẢN PHẨM
        if action == "add_product":
            name = request.form["name"]
            stock = int(request.form["stock"])

            c.execute(
                "INSERT INTO products (name, stock) VALUES (?, ?)",
                (name, stock)
            )

        # 2️⃣ BÁN HÀNG
        elif action == "sell":
            product_id = int(request.form["product_id"])
            quantity = int(request.form["quantity"])
            today = date.today().isoformat()

            c.execute("SELECT stock FROM products WHERE id = ?", (product_id,))
            stock = c.fetchone()[0]

            if quantity <= stock:
                c.execute(
                    "INSERT INTO sales (product_id, quantity, sale_date) VALUES (?, ?, ?)",
                    (product_id, quantity, today)
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

        conn.commit()
        return redirect("/")

    # GET
    c.execute("SELECT id, name, stock FROM products")
    products = c.fetchall()
    conn.close()

    return render_template("index.html", products=products)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

