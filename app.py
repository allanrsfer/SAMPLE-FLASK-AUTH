from flask import Flask, jsonify, request
from database import db
from login_manager import (
    login_manager,
    login_user,
    current_user,
    logout_user,
    login_required,
)
from models.user import User


app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"


db.init_app(app)
login_manager.init_app(app)

login_manager.login_view = "login"  # type: ignore


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route("/login", methods=["POST"])
def login():
    if not request.is_json:
        return jsonify({"error": "A solicitação deve ser em JSON"}), 400

    data = request.json

    if data is None or "username" not in data or "password" not in data:
        return jsonify({"error": "Nao encontrado username ou password"}), 400

    username = data.get("username")
    password = data.get("password")

    if username and password:
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            login_user(user)
            print(current_user.is_authenticated)
            return jsonify({"message": "Autenticação realizada com sucesso"})

    return jsonify({"message": "Credenciais incorretas"}), 400


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout realizado com sucesso"})


@app.route("/user", methods=["POST"])
@login_required
def user():
    if not request.is_json:
        return jsonify({"error": "A solicitação deve ser em JSON"}), 400

    data = request.json

    if data is None or "username" not in data or "password" not in data:
        return jsonify({"error": "Nao encontrado username ou password"}), 400

    username = data.get("username")
    password = data.get("password")

    if username and password:
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "Usuário cadastrado com sucesso"}), 201

    return jsonify({"message": "Dados inválidos"}), 400


@app.route("/user/<int:id_user>", methods=["GET"])
@login_required
def read_user(id_user):
    user = User.query.get(id_user)

    if user:
        return {"username": user.username}

    return jsonify({"message": "Usuário nao encontrado"}), 404


@app.route("/user/<int:id_user>", methods=["PUT"])
@login_required
def update_user(id_user):
    user = User.query.get(id_user)

    if user:
        return {"username": user.username}

    return jsonify({"message": "Usuário nao encontrado"}), 404


if __name__ == "__main__":
    app.run(debug=True)
