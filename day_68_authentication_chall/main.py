import string
from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory, Response
from typing import Union
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'

# CREATE DATABASE


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# CREATE TABLE IN DB


class User(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))


with app.app_context():
    db.create_all()


@app.route('/')
def home() -> str:
    print(render_template("index.html"))
    return render_template("index.html")


@app.route('/register', methods=["GET", "POST"])
def register() -> Union[Response, str]:
    if request.method == "POST":
        new_user = User(
            email=request.form.get("email"): str,
            name=request.form.get("name"): str,
            password=request.form.get("password"): str
            )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("secrets", user=new_user: User))
    return render_template("register.html")


@app.route('/login', methods=["GET", "POST"])
def login() -> str:
    return render_template("login.html")


@app.route('/secrets')
def secrets() -> str:
    return render_template("secrets.html")


@app.route('/logout')
def logout() -> None:
    pass


@app.route('/download')
def download() -> Response:
    return send_from_directory("static", "files/cheat_sheet.pdf")


if __name__ == "__main__":
    app.run(debug=True)
