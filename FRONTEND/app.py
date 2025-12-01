from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

# Cambia esto según tu entorno
#API_URL = "http://127.0.0.1:5000"   # backend local
API_URL = "http://alb-project-1386641155.us-east-1.elb.amazonaws.com"



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
    res = requests.get(f"{API_URL}/products")
    data = res.json()
    return render_template("products.html", products=data)


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


# =====================
#   USERS
# =====================
@app.route("/users")
def users():
    res = requests.get(f"{API_URL}/users")
    data = res.json()
    return render_template("users.html", users=data)

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

if __name__ == "__main__":
    app.run(debug=True, port=3000)
