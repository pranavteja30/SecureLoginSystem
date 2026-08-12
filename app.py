from flask import Flask, render_template, request, redirect, url_for, session
import os
import bcrypt
import pyotp
import qrcode
import io
import base64

from dotenv import load_dotenv

from database import init_database, create_user, get_user, get_connection

load_dotenv()

app = Flask(__name__)

# Secret key used to protect Flask sessions.
# Replace this with a long random value before deployment.
app.secret_key = os.environ["SECRET_KEY"]


init_database()


def generate_qr_code(secret, username):
    totp = pyotp.TOTP(secret)

    provisioning_uri = totp.provisioning_uri(
        name=username,
        issuer_name="Secure Login System"
    )

    qr = qrcode.make(provisioning_uri)

    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")

    return base64.b64encode(buffer.getvalue()).decode("utf-8")


@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            return "Username and password are required."

        if len(username) < 3 or len(username) > 30:
            return "Username must be between 3 and 30 characters."

        if len(password) < 8:
            return "Password must contain at least 8 characters."

        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        )

        if not create_user(username, password_hash.decode("utf-8")):
            return "Username already exists."

        return redirect(url_for("login"))

    return render_template("register.html")\

@app.route("/setup-2fa", methods=["GET", "POST"])
def setup_2fa():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user = get_user(session["username"])

    if request.method == "POST":

        code = request.form.get("code", "").strip()

        if not code:
            return "Verification code is required."

        totp = pyotp.TOTP(user["two_factor_secret"])

        if totp.verify(code):

            connection = get_connection()

            connection.execute(
                """
                UPDATE users
                SET two_factor_enabled = 1
                WHERE id = ?
                """,
                (user["id"],)
            )

            connection.commit()
            connection.close()

            return redirect(url_for("dashboard"))

        return "Invalid verification code."

    if not user["two_factor_secret"]:

        secret = pyotp.random_base32()

        connection = get_connection()

        connection.execute(
            """
            UPDATE users
            SET two_factor_secret = ?
            WHERE id = ?
            """,
            (secret, user["id"])
        )

        connection.commit()
        connection.close()

        user = get_user(session["username"])

    qr_code = generate_qr_code(
        user["two_factor_secret"],
        user["username"]
    )

    return render_template(
        "setup_2fa.html",
        qr_code=qr_code,
        secret=user["two_factor_secret"]
    )


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = get_user(username)

        if user and bcrypt.checkpw(
            password.encode("utf-8"),
            user["password_hash"].encode("utf-8")
        ):

            session.clear()

            if user["two_factor_enabled"]:

                session["pending_2fa_user_id"] = user["id"]
                session["pending_2fa_username"] = user["username"]

                return redirect(url_for("verify_2fa"))

            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["two_factor_verified"] = True

            return redirect(url_for("dashboard"))

        return "Invalid username or password."

    return render_template("login.html")

@app.route("/verify-2fa", methods=["GET", "POST"])
def verify_2fa():

    if "pending_2fa_user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["pending_2fa_user_id"]
    username = session["pending_2fa_username"]

    user = get_user(username)

    if not user:
        session.clear()
        return redirect(url_for("login"))

    if request.method == "POST":

        code = request.form.get("code", "").strip()

        if not code:
            return "Verification code is required."

        totp = pyotp.TOTP(user["two_factor_secret"])

        if totp.verify(code):

            session.clear()

            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["two_factor_verified"] = True

            return redirect(url_for("dashboard"))

        return "Invalid authentication code."

    return render_template("verify_2fa.html")

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if not session.get("two_factor_verified", False):
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        username=session["username"]
    )

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)