import os
from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Config desde variables de entorno (pon las de tu RDS)
DB_HOST = os.getenv("DB_HOST", "db-instancia-project.cgl84qec82qv.us-east-1.rds.amazonaws.com")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "admin")
DB_PASS = os.getenv("DB_PASS", "123456789aA")
DB_NAME = os.getenv("DB_NAME", "test")

def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        autocommit=True
    )


# -------------------------
# INICIALIZACIÓN DE BASE DE DATOS
# -------------------------

def init_database():
    """
    Crea las tablas users y products si no existen,
    e inserta 2 registros de ejemplo en cada una si están vacías.
    """
    try:
        print(" Inicializando base de datos...")
        con = get_connection()
        cursor = con.cursor()
        
        # ====== CREAR TABLA USERS ======
        print(" Creando tabla 'users' si no existe...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(100) NOT NULL,
                age INT,
                gender CHAR(1) CHECK (gender IN ('M', 'F'))
            );
        """)
        print(" Tabla 'users' verificada/creada")
        
        # Verificar si la tabla users está vacía
        cursor.execute("SELECT COUNT(*) FROM users;")
        user_count = cursor.fetchone()[0]
        
        if user_count == 0:
            print(" Insertando registros de ejemplo en 'users'...")
            cursor.execute("""
                INSERT INTO users (name, age, gender) VALUES
                ('Juan Pérez', 25, 'M'),
                ('María García', 30, 'F');
            """)
            print(" 2 usuarios de ejemplo insertados")
        else:
            print(f"La tabla 'users' ya tiene {user_count} registro(s)")
        
        # ====== CREAR TABLA PRODUCTS ======
        print("📋 Creando tabla 'products' si no existe...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(100) NOT NULL,
                price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
                tax DECIMAL(10, 2) NOT NULL DEFAULT 0.00
            );
        """)
        print("Tabla 'products' verificada/creada")
        
        # Verificar si la tabla products está vacía
        cursor.execute("SELECT COUNT(*) FROM products;")
        product_count = cursor.fetchone()[0]
        
        if product_count == 0:
            print("Insertando registros de ejemplo en 'products'...")
            cursor.execute("""
                INSERT INTO products (name, price, tax) VALUES
                ('Laptop Dell XPS 15', 1599.99, 95.99),
                ('Mouse Logitech MX Master', 99.99, 7.00);
            """)
            print(" 2 productos de ejemplo insertados")
        else:
            print(f"  La tabla 'products' ya tiene {product_count} registro(s)")
        
        cursor.close()
        con.close()
        print("Base de datos inicializada correctamente\n")
        
    except Error as e:
        print(f" Error al inicializar base de datos: {e}")
    except Exception as e:
        print(f" Error inesperado: {e}")


# -------------------------
# RUTAS PRODUCTS
# -------------------------

@app.route("/products", methods=["GET"])
def list_products():
    try:
        con = get_connection()
        cursor = con.cursor()
        cursor.execute("SELECT id, name, price, tax FROM products;")
        rows = cursor.fetchall()
        cursor.close()
        con.close()
        products = [{"id": r[0], "name": r[1], "price": float(r[2]), "tax": float(r[3])} for r in rows]
        return jsonify(products), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/products/<int:item_id>", methods=["GET"])
def get_product(item_id):
    try:
        con = get_connection()
        cursor = con.cursor()
        cursor.execute("SELECT id, name, price, tax FROM products WHERE id = %s;", (item_id,))
        row = cursor.fetchone()
        cursor.close()
        con.close()
        if not row:
            return jsonify({"error": "Product not found"}), 404
        product = {"id": row[0], "name": row[1], "price": float(row[2]), "tax": float(row[3])}
        return jsonify(product), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/products", methods=["POST"])
def create_product():
    data = request.get_json(force=True)
    name = data.get("name")
    price = data.get("price", 0)
    tax = data.get("tax", 0)
    if not name:
        return jsonify({"error": "name is required"}), 400
    try:
        con = get_connection()
        cursor = con.cursor()
        cursor.execute("INSERT INTO products (name, price, tax) VALUES (%s, %s, %s);", (name, price, tax))
        new_id = cursor.lastrowid
        cursor.close()
        con.close()
        return jsonify({"id": new_id, "name": name, "price": price, "tax": tax}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/products/<int:item_id>", methods=["PUT"])
def update_product(item_id):
    data = request.get_json(force=True)
    name = data.get("name")
    price = data.get("price")
    tax = data.get("tax")
    try:
        con = get_connection()
        cursor = con.cursor()
        # verifica existencia
        cursor.execute("SELECT id FROM products WHERE id = %s;", (item_id,))
        if not cursor.fetchone():
            cursor.close()
            con.close()
            return jsonify({"error": "Product not found"}), 404
        # actualiza solo campos enviados
        updates = []
        params = []
        if name is not None:
            updates.append("name = %s"); params.append(name)
        if price is not None:
            updates.append("price = %s"); params.append(price)
        if tax is not None:
            updates.append("tax = %s"); params.append(tax)
        if updates:
            sql = "UPDATE products SET " + ", ".join(updates) + " WHERE id = %s;"
            params.append(item_id)
            cursor.execute(sql, tuple(params))
        cursor.close()
        con.close()
        return jsonify({"message": "Product updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/products/<int:item_id>", methods=["DELETE"])
def delete_product(item_id):
    try:
        con = get_connection()
        cursor = con.cursor()
        cursor.execute("DELETE FROM products WHERE id = %s;", (item_id,))
        affected = cursor.rowcount
        cursor.close()
        con.close()
        if affected == 0:
            return jsonify({"error": "Product not found"}), 404
        return jsonify({"message": "Product deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------
# RUTAS USERS
# -------------------------

@app.route("/users", methods=["GET"])
def list_users():
    try:
        con = get_connection()
        cursor = con.cursor()
        cursor.execute("SELECT id, name, age, gender FROM users;")
        rows = cursor.fetchall()
        cursor.close()
        con.close()
        users = [{"id": r[0], "name": r[1], "age": r[2], "gender": r[3]} for r in rows]
        return jsonify(users), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    try:
        con = get_connection()
        cursor = con.cursor()
        cursor.execute("SELECT id, name, age, gender FROM users WHERE id = %s;", (user_id,))
        row = cursor.fetchone()
        cursor.close()
        con.close()
        if not row:
            return jsonify({"error": "User not found"}), 404
        user = {"id": row[0], "name": row[1], "age": row[2], "gender": row[3]}
        return jsonify(user), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json(force=True)
    name = data.get("name")
    age = data.get("age")
    gender = data.get("gender")
    
    # Validación de campos
    if not name:
        return jsonify({"error": "name is required"}), 400
    if gender and gender not in ['M', 'F']:
        return jsonify({"error": "gender must be 'M' or 'F'"}), 400
    
    try:
        con = get_connection()
        cursor = con.cursor()
        cursor.execute("INSERT INTO users (name, age, gender) VALUES (%s, %s, %s);", (name, age, gender))
        new_id = cursor.lastrowid
        cursor.close()
        con.close()
        return jsonify({"id": new_id, "name": name, "age": age, "gender": gender}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.get_json(force=True)
    name = data.get("name")
    age = data.get("age")
    gender = data.get("gender")
    
    # Validación de gender
    if gender and gender not in ['M', 'F']:
        return jsonify({"error": "gender must be 'M' or 'F'"}), 400
    
    try:
        con = get_connection()
        cursor = con.cursor()
        cursor.execute("SELECT id FROM users WHERE id = %s;", (user_id,))
        if not cursor.fetchone():
            cursor.close()
            con.close()
            return jsonify({"error": "User not found"}), 404
        updates = []
        params = []
        if name is not None:
            updates.append("name = %s"); params.append(name)
        if age is not None:
            updates.append("age = %s"); params.append(age)
        if gender is not None:
            updates.append("gender = %s"); params.append(gender)
        if updates:
            sql = "UPDATE users SET " + ", ".join(updates) + " WHERE id = %s;"
            params.append(user_id)
            cursor.execute(sql, tuple(params))
        cursor.close()
        con.close()
        return jsonify({"message": "User updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    try:
        con = get_connection()
        cursor = con.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s;", (user_id,))
        affected = cursor.rowcount
        cursor.close()
        con.close()
        if affected == 0:
            return jsonify({"error": "User not found"}), 404
        return jsonify({"message": "User deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Health check
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


init_database()
if __name__ == "__main__":
    # Iniciar servidor Flask
    app.run(host="0.0.0.0", port=5000, debug=True)