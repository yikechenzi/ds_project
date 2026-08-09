"""
数据库模块 - SQLite 本地存储
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "xuanping.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL DEFAULT '线上',
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            purchase_price REAL DEFAULT 0,
            shipping_cost REAL DEFAULT 0,
            link TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE CASCADE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            sale_price REAL DEFAULT 0,
            quantity INTEGER DEFAULT 1,
            profit REAL DEFAULT 0,
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


class SupplierDAO:
    @staticmethod
    def get_all():
        conn = get_connection()
        rows = conn.execute("SELECT * FROM suppliers ORDER BY created_at DESC").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def add(name, stype, notes=""):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO suppliers (name, type, notes) VALUES (?, ?, ?)", (name, stype, notes))
        conn.commit()
        conn.close()

    @staticmethod
    def update(sid, name, stype, notes=""):
        conn = get_connection()
        conn.execute(
            "UPDATE suppliers SET name=?, type=?, notes=? WHERE id=?",
            (name, stype, notes, sid),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def delete(sid):
        conn = get_connection()
        conn.execute("DELETE FROM suppliers WHERE id = ?", (sid,))
        conn.commit()
        conn.close()

    @staticmethod
    def count():
        conn = get_connection()
        row = conn.execute("SELECT COUNT(*) as cnt FROM suppliers").fetchone()
        conn.close()
        return row["cnt"]


class ProductDAO:
    @staticmethod
    def get_all():
        conn = get_connection()
        rows = conn.execute("""
            SELECT p.*, s.name as supplier_name
            FROM products p LEFT JOIN suppliers s ON p.supplier_id = s.id
            ORDER BY p.created_at DESC
        """).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def add(supplier_id, name, purchase_price, shipping_cost, link=""):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO products (supplier_id, name, purchase_price, shipping_cost, link) VALUES (?, ?, ?, ?, ?)",
            (supplier_id, name, purchase_price, shipping_cost, link),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def update(pid, supplier_id, name, purchase_price, shipping_cost, link=""):
        conn = get_connection()
        conn.execute(
            "UPDATE products SET supplier_id=?, name=?, purchase_price=?, shipping_cost=?, link=? WHERE id=?",
            (supplier_id, name, purchase_price, shipping_cost, link, pid),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def delete(pid):
        conn = get_connection()
        conn.execute("DELETE FROM products WHERE id = ?", (pid,))
        conn.commit()
        conn.close()

    @staticmethod
    def count():
        conn = get_connection()
        row = conn.execute("SELECT COUNT(*) as cnt FROM products").fetchone()
        conn.close()
        return row["cnt"]


class OrderDAO:
    @staticmethod
    def get_all():
        conn = get_connection()
        rows = conn.execute("""
            SELECT o.*, p.name as product_name, p.purchase_price, p.shipping_cost,
                   s.name as supplier_name
            FROM orders o
            LEFT JOIN products p ON o.product_id = p.id
            LEFT JOIN suppliers s ON p.supplier_id = s.id
            ORDER BY o.created_at DESC
        """).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def add(product_id, sale_price, quantity, profit, notes=""):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO orders (product_id, sale_price, quantity, profit, notes) VALUES (?, ?, ?, ?, ?)",
            (product_id, sale_price, quantity, profit, notes),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def update(oid, product_id, sale_price, quantity, profit, notes=""):
        conn = get_connection()
        conn.execute(
            "UPDATE orders SET product_id=?, sale_price=?, quantity=?, profit=?, notes=? WHERE id=?",
            (product_id, sale_price, quantity, profit, notes, oid),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def delete(oid):
        conn = get_connection()
        conn.execute("DELETE FROM orders WHERE id = ?", (oid,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_stats():
        conn = get_connection()
        total_orders = conn.execute("SELECT COUNT(*) as cnt FROM orders").fetchone()["cnt"]
        total_profit = conn.execute("SELECT COALESCE(SUM(profit), 0) as s FROM orders").fetchone()["s"]
        total_sales = conn.execute("SELECT COALESCE(SUM(sale_price * quantity), 0) as s FROM orders").fetchone()["s"]
        total_cost = conn.execute("SELECT COALESCE(SUM( (p.purchase_price + p.shipping_cost) * o.quantity ), 0) as s FROM orders o LEFT JOIN products p ON o.product_id = p.id").fetchone()["s"]

        today = conn.execute("""
            SELECT COALESCE(SUM(profit), 0) as s FROM orders
            WHERE DATE(created_at) = DATE('now')
        """).fetchone()["s"]
        conn.close()
        return {
            "total_orders": total_orders,
            "total_profit": round(total_profit, 2),
            "total_sales": round(total_sales, 2),
            "total_cost": round(total_cost, 2),
            "today_profit": round(today, 2),
        }
