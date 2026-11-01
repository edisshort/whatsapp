from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from routes.auth_helpers import check_login

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("logged_in"):
        return redirect(url_for("dashboard.index"))
    if request.method == "POST":
        if check_login(request.form.get("username", ""), request.form.get("password", "")):
            session["logged_in"] = True
            return redirect(url_for("dashboard.index"))
        flash("Invalid login", "danger")
    return render_template("login.html")


@auth_bp.route("/logout", methods=["GET", "POST"])
def logout():
    if request.method == "POST" and request.form.get("clear_local") == "yes":
        from services.local_data import clear_all_local_data

        clear_all_local_data()
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("auth.login"))
