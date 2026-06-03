from flask import Flask, request, render_template, session, redirect, send_file, jsonify
import os, json

APP_SECRET_KEY = "abc123"
SAVE_DIR = "./"

app = Flask(__name__)
app.secret_key = APP_SECRET_KEY

@app.route("/")
def root():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    target_path = request.form.get("target_path")

    names = request.form.getlist("category_name[]")
    paths = request.form.getlist("category_path[]")
    binds = request.form.getlist("category_bind[]")

    categories = [
        {"name": n, "path": p, "bind": b}
        for n, p, b in zip(names, paths, binds)
    ]

    session["pathes"] = {
        "target_path": target_path,
        "categories": categories
    }
    session["is_initiated"] = True

    return redirect("/dashboard")

@app.route("/dashboard", methods=["GET"])
def dashboard():
    if not session.get("is_initiated", False):
        return redirect("/")
    
    pathes = session.get("pathes", None)

    if pathes == None:
        return redirect("/")
    
    target_directory = pathes.get("target_path")
    categories = pathes.get("categories")

    session["target_directory"] = target_directory
    session["categories"] = categories
    
    return render_template("dashboard.html")


@app.route("/get-files", methods=["GET"])
def get_item():
    if os.listdir(session.get("target_directory")):
        return os.listdir(session.get("target_directory"))
    return redirect("/")

@app.route("/get-categories", methods=["GET"])
def get_categories():
    if session.get("categories"):
        return session.get("categories")
    return redirect("/")

@app.route("/get-file/<path:file>")
def get_file(file):
    return send_file(os.path.join(session.get("target_directory"), file))

@app.route("/save-state", methods=["POST"])
def save_state():
    data = request.json

    target_path = session.get("target_path")
    data["target_path"] = target_path

    save_name = data.get("name")
    with open(f"{os.path.join(SAVE_DIR)}/{save_name}.json", "w") as f:
        json.dump(data, f)
    return jsonify({"status": "ok"})


@app.route("/load-state")
def load_state():

    save_name = request.args.get("name")

    if not os.path.exists({os.path.join(SAVE_DIR)}/{save_name}.json):
        return jsonify({"error": "file not found"}), 404

    with open({os.path.join(SAVE_DIR)}/{save_name}.json) as f:
        data = json.load(f)

    return jsonify(data)


if __name__ == "__main__":
    app.run("127.0.0.1", 8080)