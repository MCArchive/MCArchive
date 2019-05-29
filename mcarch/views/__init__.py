import json

from flask import Blueprint, render_template, url_for, redirect, abort, flash
from sqlalchemy.exc import IntegrityError

from mcarch.app import db
#from mcarch.model import Channel
from mcarch.forms import NewChanForm

root = Blueprint('root', __name__, template_folder="templates")

@root.route("/")
def home():
    return render_template("home.html")

