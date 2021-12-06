from enum import unique
from typing import Text
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from util import sendEmail
from sqlalchemy import func

app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:projectdb@localhost/height_collector"
db = SQLAlchemy(app)

class Data(db.Model):
    __tablename__ = "data"
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(120), unique = True)
    height = db.Column(db.Integer)

    def __init__(self, email, height) -> None:
        self.email = email
        self.height = height



@app.route("/")
def index():
    return render_template("index.html")

@app.route("/success", methods=["POST"])
def success():
    if request.method == 'POST':
        email = request.form["email_name"]
        height = request.form["height_name"]
        if db.session.query(Data).filter(Data.email == email).count() == 0:
            data = Data(email, height)
            db.session.add(data)
            db.session.commit()
            # db.session.query(Data).all()
            averageHeight = db.session.query(func.avg(Data.height)).scalar()
            averageHeight = round(averageHeight, 2)
            count = db.session.query(Data).count()
            sendEmail(email, height, averageHeight, count)
            return render_template("success.html")
    return render_template("index.html", text= "We already have that email on record!")

if __name__ == "__main__":
    app.debug = True
    app.run()


