import os
from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

# Cambia esto según tu entorno
# Cambia esto según tu entorno
API_URL = os.getenv("API_URL", "http://alb-project-1386641155.us-east-1.elb.amazonaws.com")



# =====================
#   HOME
# =====================
@app.route("/")
def index():
    return render_template("index.html")


# =====================
#   PRODUCTS
# =====================
@app.route("/products")
def products():
    try:
        res = requests.get(f"{API_URL}/products")
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, list):
                return render_template("products.html", products=data)
        # Fallback for error or non-list response
        return render_template("products.html", products=[], error="Could not load products")
    except Exception:
        return render_template("products.html", products=[], error="Backend unavailable")


@app.route("/products/create", methods=["GET", "POST"])
def create_product():
    if request.method == "POST":
        payload = {
            "name": request.form["name"],
            "price": float(request.form["price"]),
            "tax": float(request.form["tax"])
        }
        requests.post(f"{API_URL}/products", json=payload)
        return redirect(url_for("products"))
    return render_template("create_product.html")


@app.route("/products/edit/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    if request.method == "POST":
        payload = {
            "name": request.form["name"],
            "price": float(request.form["price"]),
            "tax": float(request.form["tax"])
        }
        requests.put(f"{API_URL}/products/{product_id}", json=payload)
        return redirect(url_for("products"))
    
    # GET: Fetch product data to pre-fill form
    res = requests.get(f"{API_URL}/products/{product_id}")
    if res.status_code == 200:
        product = res.json()
        return render_template("create_product.html", product=product)
    return redirect(url_for("products"))


@app.route("/products/delete/<int:product_id>", methods=["POST"])
def delete_product(product_id):
    requests.delete(f"{API_URL}/products/{product_id}")
    return redirect(url_for("products"))


# =====================
#   USERS
# =====================
@app.route("/users")
def users():
    try:
        res = requests.get(f"{API_URL}/users")
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, list):
                return render_template("users.html", users=data)
        return render_template("users.html", users=[], error="Could not load users")
    except Exception:
        return render_template("users.html", users=[], error="Backend unavailable")

@app.route("/users/create", methods=["GET", "POST"])
def create_user():
    if request.method == "POST":
        payload = {
            "name": request.form["name"],
            "age": int(request.form["age"]),
            "gender": request.form["gender"]
        }
        requests.post(f"{API_URL}/users", json=payload)
        return redirect(url_for("users"))
    return render_template("create_user.html")


@app.route("/users/edit/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    if request.method == "POST":
        payload = {
            "name": request.form["name"],
            "age": int(request.form["age"]),
            "gender": request.form["gender"]
        }
        requests.put(f"{API_URL}/users/{user_id}", json=payload)
        return redirect(url_for("users"))
    
    # GET: Fetch user data to pre-fill form
    res = requests.get(f"{API_URL}/users/{user_id}")
    if res.status_code == 200:
        user = res.json()
        return render_template("create_user.html", user=user)
    return redirect(url_for("users"))


@app.route("/users/delete/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    requests.delete(f"{API_URL}/users/{user_id}")
    return redirect(url_for("users"))

if __name__ == "__main__":
    app.run(debug=True, port=3000)
