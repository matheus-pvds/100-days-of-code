import string
from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

#CREATE FLASK_APP


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'

#CREATE FLASK_LOGIN_MANAGER


login_manager = LoginManager()
login_manager.init_app(app)

# CREATE DATABASE


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CREATE TABLE IN DB


class User(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))


with app.app_context():
    db.create_all()

#PROPERTIES FOR LOGIN_MANAGER
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

#APP ROUTES


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            new_user = User(
            email=request.form.get("email"),
            name=request.form.get("name"),
            password=(generate_password_hash(
                request.form.get("password"), 
                method='pbkdf2:sha256', 
                salt_length=8
                ))
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for("secrets", user=new_user.name))
        except:
            flash("User already exists")
            return redirect(url_for("login"))
    return render_template("register.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    form = request.form
    if request.method == "POST":
        email = form.get("email")
        password = form.get("password")
        user = db.session.execute(
            db.select(User).where(User.email == email)
            ).scalar()
        if user and check_password_hash(user.password, password):
            try:
                login_user(user)
                return redirect(url_for("secrets", user=user.name))
            except:
                return redirect(url_for("login"))
        else:
            if not user:
                flash("User does not exist")
            else:
                flash("Incorrect password")
            return redirect(url_for("login"))
    return render_template("login.html")


@app.route('/secrets')
@login_required
def secrets():
    return render_template("secrets.html", )


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/download')
def download():
    return send_from_directory("static", "files/cheat_sheet.pdf")


if __name__ == "__main__":
    app.run(debug=True)
