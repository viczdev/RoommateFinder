
from flask import Flask, render_template, request, session, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import redirect
from util import sendEmail
from sqlalchemy import func
from google_auth_oauthlib.flow import Flow
import os
import google.auth.transport.requests
from google.oauth2 import id_token
import requests
from pip._vendor import cachecontrol

app=Flask(__name__)
app.secret_key = "vztest"
GOOGLE_CLIENT_ID = "1019293070047-f5u3dfe3uu3tten7g66o5cp0a3ceuiee.apps.googleusercontent.com"
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:projectdb@localhost/roommate"
db = SQLAlchemy(app)


clientSecretsFile = os.path.join(os.getcwd(), "client_secret.json")


flow = Flow.from_client_secrets_file(client_secrets_file=clientSecretsFile, 
                                    scopes=["https://www.googleapis.com/auth/userinfo.profile", 
                                    "https://www.googleapis.com/auth/userinfo.email", "openid"],
                                    redirect_uri = "http://127.0.0.1:5000/callback")

def loginRequired(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            abort(401)
        else:
            return function()
    wrapper.__name__ = function.__name__
    return wrapper


class Data(db.Model):
    __tablename__ = "data"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(120), unique = True)
    gender = db.Column(db.String(20))
    budget = db.Column(db.Integer)
    req = db.Column(db.String(300))

    def __init__(self, name, email, gender, budget, req) -> None:
        self.name = name
        self.email = email
        self.gender = gender
        self.budget = budget
        self.req = req

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    authorizationURL, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorizationURL)

@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response = request.url)
    if not session["state"] == request.args["state"]:
        abort(500)
    credentials = flow.credentials
    requestSession = requests.session()
    cachedSession = cachecontrol.CacheControl(requestSession)
    tokenRequest = google.auth.transport.requests.Request(session=cachedSession)
    idInfo = id_token.verify_oauth2_token(
        id_token = credentials.id_token,
        request = tokenRequest,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = idInfo.get("sub")
    session["name"] = idInfo.get("name")
    session["email"] = idInfo.get("email")
    return redirect("/main")    


@app.route("/main")
@loginRequired
def main():
    return render_template("main.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/success", methods=["POST"])
def success():
    if request.method == 'POST':
        name = request.form["name"]
        email = session["email"]
        gender = request.form["gender"]
        budget = request.form["budget"]
        requirements = request.form["requirements"]
        
        if db.session.query(Data).filter(Data.email == email).count() == 0:
            data = Data(name, email, gender, budget, requirements)
            db.session.add(data)
            db.session.commit()
            return render_template("success.html", text="submission")
        else:
            info = db.session.query(Data).filter_by(email = email).first()
            info.name = name
            info.email = email
            info.gender = gender
            info.budget = budget
            info.req = requirements
            db.session.commit()
            return render_template("success.html", text="update")

    return render_template("main.html", text= "Something went wrong, please check inputs or contact the admin.")

@app.route("/content")
@loginRequired
def content():
    data = db.session.query(Data).all()
    return render_template("content.html", data=data)

if __name__ == "__main__":
    app.debug = True
    app.run()
