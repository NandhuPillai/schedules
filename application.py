import os

import datetime
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session

from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, apology

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

#Setting a Secret Key
app.config["SECRET_KEY"] = "secret"

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///final.db")

@app.route("/")
@login_required
def index():
    """Index page with schedule"""
    schedule_type = db.execute("SELECT type FROM user_scheduletype WHERE user_id = :id ORDER BY id DESC LIMIT 1", id = session["user_id"])

    if schedule_type == []:

        return render_template("none.html")

    user_type = schedule_type[0]["type"]

    if user_type == 7:
        schedule_data = db.execute("SELECT period_name, start_time, finish_time FROM user_schedule WHERE user_id = :id AND day = :day ORDER BY id DESC LIMIT 7;", id = session["user_id"], day = "A")

        bday_check = db.execute("SELECT period_num, period_name, start_time, finish_time FROM user_schedule WHERE user_id = :id AND day = :day ORDER BY id DESC LIMIT 7;", id = session["user_id"], day = "B")

        if bday_check[0]["period_name"] == []:
            print("hi, world")
        else:
            bperiod = bday_check[0]["period_name"]
            bperiod_num = bday_check[0]["period_num"]
            bperiod_start = bday_check[0]["start_time"]
            bperiod_finish = bday_check[0]["finish_time"]

        return render_template("7_index.html", bperiod = bperiod, bperiod_num = bperiod_num, bperiod_start = bperiod_start, bperiod_finish = bperiod_finish, period1 = schedule_data[6]["period_name"], period2 = schedule_data[5]["period_name"], period3 = schedule_data[4]["period_name"], period4 = schedule_data[3]["period_name"], period5 = schedule_data[2]["period_name"], period6 = schedule_data[1]["period_name"], period7 = schedule_data[0]["period_name"], period1_stime = schedule_data[6]["start_time"], period2_stime = schedule_data[5]["start_time"], period3_stime = schedule_data[4]["start_time"], period4_stime = schedule_data[3]["start_time"], period5_stime = schedule_data[2]["start_time"], period6_stime = schedule_data[1]["start_time"], period7_stime = schedule_data[0]["start_time"], period1_ftime = schedule_data[6]["finish_time"], period2_ftime = schedule_data[5]["finish_time"], period3_ftime = schedule_data[4]["finish_time"], period4_ftime = schedule_data[3]["finish_time"], period5_ftime = schedule_data[2]["finish_time"], period6_ftime = schedule_data[1]["finish_time"], period7_ftime = schedule_data[0]["finish_time"])

    else:
        today = datetime.date.today()
        semester2 = datetime.date(2021, 1, 28)
        if today < semester2:

            schedule_data = db.execute("SELECT period_name, start_time, finish_time FROM user_schedule WHERE user_id = :id AND day = :day ORDER BY id DESC LIMIT 4;", id = session["user_id"], day = "A")
            return render_template("4_index.html", period1 = schedule_data[3]["period_name"], period2 = schedule_data[2]["period_name"], period3 = schedule_data[1]["period_name"], period4 = schedule_data[0]["period_name"], period1_stime = schedule_data[3]["start_time"], period2_stime = schedule_data[2]["start_time"], period3_stime = schedule_data[1]["start_time"], period4_stime = schedule_data[0]["start_time"], period1_ftime = schedule_data[3]["finish_time"], period2_ftime = schedule_data[2]["finish_time"], period3_ftime = schedule_data[1]["finish_time"], period4_ftime = schedule_data[0]["finish_time"])

        else:

            schedule_data = db.execute("SELECT period_name, start_time, finish_time FROM user_schedule WHERE user_id = :id AND day = :day ORDER BY id DESC LIMIT 4;", id = session["user_id"], day = "B")
            return render_template("4_index.html", period1 = schedule_data[3]["period_name"], period2 = schedule_data[2]["period_name"], period3 = schedule_data[1]["period_name"], period4 = schedule_data[0]["period_name"], period1_stime = schedule_data[3]["start_time"], period2_stime = schedule_data[2]["start_time"], period3_stime = schedule_data[1]["start_time"], period4_stime = schedule_data[0]["start_time"], period1_ftime = schedule_data[3]["finish_time"], period2_ftime = schedule_data[2]["finish_time"], period3_ftime = schedule_data[1]["finish_time"], period4_ftime = schedule_data[0]["finish_time"])

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get("username")

        password = request.form.get("password")

        cpassword = request.form.get("cpassword")

        rows = db.execute("SELECT * FROM users WHERE username = :username", username=username)

        if not username:
            return apology("must provide username", 403)
        elif not password:
            return apology("must provide password", 403)

        elif " " in username or " " in password:
            return apology("no spaces allowed in username or password", 403)

        elif len(rows) != 0:
            return apology("username already exists", 403)

        elif password != cpassword:
            return apology("passwords don't match", 403)

        password = generate_password_hash(request.form.get("password"))

        db.execute("INSERT INTO users(username, hash) VALUES (:username,:password)", username=username, password=password)
        return redirect("/login")

@app.route("/choose", methods=["GET", "POST"])
def choose():

    if request.method == "POST":
        if request.form["schedtype"] == "seven":
            return redirect("/7period")
        else:
            return redirect("/4period")

    else:
        return render_template("createchoice.html")

@app.route("/7period", methods=["GET", "POST"])
def sevenperiod():

    if request.method == "POST":

        for i in range(1,8):
            APeriodName = request.form.get(str(i)+"name")
            StartTime =  request.form.get("speriod"+str(i))
            EndTime =  request.form.get("fperiod"+str(i))
            BPeriodName = request.form.get("b"+str(i)+"name")

            db.execute("INSERT into user_schedule(user_id, period_name, start_time, finish_time, period_num, day, schedule_type) VALUES (:user_id, :period_name, :start_time, :finish_time, :period_num, :day, :schedule_type)", user_id = session["user_id"], period_name=APeriodName, start_time=StartTime,finish_time=EndTime,period_num=i,day="A",schedule_type=7)
            db.execute("INSERT into user_scheduletype(user_id, type) VALUES(:user_id, :type)", user_id = session["user_id"], type = 7)
            if BPeriodName != "":
                db.execute("INSERT into user_schedule(user_id, period_name, start_time, finish_time, period_num, day, schedule_type) VALUES (:user_id, :period_name, :start_time, :finish_time, :period_num, :day, :schedule_type)", user_id = session["user_id"], period_name=BPeriodName, start_time=StartTime,finish_time=EndTime,period_num=i,day="B",schedule_type=7)
                db.execute("INSERT into user_scheduletype(user_id, type) VALUES(:user_id, :type)", user_id = session["user_id"], type = 7)

        flash("Table Created!")
        return redirect("/")
    else:
        return render_template("7period.html")

@app.route("/4period", methods=["GET", "POST"])
def fourperiod():

    if request.method == "POST":

        for i in range(1,5):
            APeriodName = request.form.get(str(i)+"name")
            StartTime =  request.form.get("speriod"+str(i))
            EndTime =  request.form.get("fperiod"+str(i))

            db.execute("INSERT into user_schedule(user_id, period_name, start_time, finish_time, period_num, day, schedule_type) VALUES (:user_id, :period_name, :start_time, :finish_time, :period_num, :day, :schedule_type)", user_id = session["user_id"], period_name=APeriodName, start_time=StartTime,finish_time=EndTime,period_num=i,day="A",schedule_type=4)
            db.execute("INSERT into user_scheduletype(user_id, type) VALUES(:user_id, :type)", user_id = session["user_id"], type = 4)

        for i in range(1,5):
            StartTime =  request.form.get("speriod"+str(i))
            EndTime =  request.form.get("fperiod"+str(i))
            BPeriodName = request.form.get("b"+str(i)+"name")

            db.execute("INSERT into user_schedule(user_id, period_name, start_time, finish_time, period_num, day, schedule_type) VALUES (:user_id, :period_name, :start_time, :finish_time, :period_num, :day, :schedule_type)", user_id = session["user_id"], period_name=BPeriodName, start_time=StartTime,finish_time=EndTime,period_num=i,day="B",schedule_type=4)
            db.execute("INSERT into user_scheduletype(user_id, type) VALUES(:user_id, :type)", user_id = session["user_id"], type = 4)

        flash("Table Created!")
        return redirect("/")

    else:
        return render_template("4period.html")
