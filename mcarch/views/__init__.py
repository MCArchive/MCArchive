import json

from flask import Blueprint, render_template, url_for, redirect, abort, flash, send_file
from sqlalchemy.exc import IntegrityError

from mcarch.app import db

root = Blueprint('root', __name__, template_folder="templates")

@root.route("/")
def home():
    return render_template("home.html")

@root.route("/robots.txt")
def robots():
    return send_file("templates/robots.txt")

@root.app_errorhandler(404)
def err404(err):
    return render_template("error/404.html"), 404

@root.app_errorhandler(403)
def err403(err):
    return render_template("error/403.html"), 403

