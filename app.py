import os

from matplotlib import ticker

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd, get_tickers

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

#Get list of symbols
ticker_list = get_tickers()


@app.route("/")
@login_required
def index():
    
    user_id = session["user_id"]
    user_purchases = db.execute("SELECT * FROM purchases WHERE id=?",user_id)

    cash_left = db.execute("SELECT cash FROM users WHERE id=?",user_id)[0]['cash']
    total_cash = 10000


    #User purchases returns a list of dicts, each a row in the purchases table
    return render_template("index.html",purchases =user_purchases,cash_left=(cash_left),total_cash =(total_cash))




@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    #If method is POST
    if request.method == "POST":
        user_id = session["user_id"]
        # Ensure username was submitted
        if not request.form.get("symbol"):
            return apology("must provide symbol", 400)
        elif not request.form.get("shares"):
            return apology("must provide number of shares", 403)

        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        if(not shares.isnumeric()):
            return apology("Please input a positive integer",400)
        else:
            shares = float(shares)
            if(shares <= 0):
                return apology("Please input a positive integer",400)

        quoted_symbol = lookup(symbol)
        if(quoted_symbol == None):
            return apology("Incorrect Symbol",400)
        price = quoted_symbol["price"]
        #If already purchased
        purchased_before = db.execute("SELECT shares FROM purchases WHERE symbol=? AND id=?",symbol.upper(),user_id)
        total_shares = int(0)
        user_current_cash = db.execute("SELECT cash FROM users WHERE id=?",user_id)[0]['cash']
        for share in purchased_before:
            total_shares += int(share["shares"])

        if(float(price) * float(shares) > user_current_cash):
            return apology("You cannot afford that",400)
        if(len(purchased_before) > 0):
            old_total = float(db.execute("SELECT total FROM purchases WHERE symbol=? AND id=?",symbol.upper(),user_id)[0]['total'])
            total_shares += int(shares)
            total = (price * float(shares)) + old_total
            db.execute("UPDATE purchases SET shares=?,total=? WHERE symbol=? AND id=?",total_shares,total,symbol.upper(),user_id)

            user_current_cash -= price * float(shares)
            db.execute("UPDATE users SET cash=? WHERE id=?",user_current_cash,user_id)


        else:

            name = quoted_symbol["name"]

            symbol = quoted_symbol["symbol"]

            total = price * float(shares)

            user_current_cash = db.execute("SELECT cash FROM users WHERE id=?",user_id)[0]['cash']




            if( total > float(user_current_cash)):
                return apology("Not enough cash",403)
            else:
                user_current_cash -= price * float(shares)
                db.execute("UPDATE users SET cash=? WHERE id=?",user_current_cash,user_id)
                db.execute("INSERT INTO purchases(symbol,name,shares,price,total,id) VALUES(?,?,?,?,?,?)",symbol,name,shares,
                (price),(total),user_id)


        db.execute("INSERT INTO history (price,symbol,shares,id) VALUES(?,?,?,?)",price,symbol,shares,
        session['user_id'])
        return redirect("/")


    else:
        return render_template("/buy.html",ticker_list=ticker_list)

@app.route("/change_password",methods=["POST","GET"])
@login_required
def change_password():

    if (request.method=="POST"):
        np = request.form.get("new_password")
        cp = request.form.get("confirm_password")



        if(np == cp):
            p = generate_password_hash(np)
            db.execute("UPDATE users SET hash=? WHERE id=?",p,session["user_id"])
            return redirect("/")
        else:
            return apology("Please Make sure passwords match")

    else:
        return render_template("change_password.html")

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    transactions = db.execute("SELECT * FROM history WHERE id=?",session["user_id"])
    return render_template("history.html",transactions=transactions)


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
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    #If method is POST
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("symbol"):
            return apology("must provide username", 400)
        symbol = request.form.get("symbol")

        quoted_symbol = lookup(symbol)
        if(quoted_symbol == None):
            return apology("Please try a valid symbol")
        name = quoted_symbol["name"]
        price = quoted_symbol["price"]
        symbol = quoted_symbol["symbol"]

        
       
        return render_template("quoted.html",name=name,price=usd(price),symbol=symbol)
    #If method is GET
    else:
        return render_template("quote.html",ticker_list=ticker_list)

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    #If method is POST
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure password was submitted
        elif not request.form.get("confirmation"):
            return apology("must confirm password", 400)


        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if(confirmation != password):
            return apology("Passwords must match",400)
        similar_username = db.execute("SELECT * FROM users WHERE username=?",username)
        if(similar_username):
            return apology("Please choose a different username",400)
        password_hash = generate_password_hash(password)

        db.execute("INSERT INTO users (username,hash) VALUES(?,?)",username,password_hash)

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        session["user_id"] = rows[0]["id"]

        return redirect("/")

    #If method is GET
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    user_id = session["user_id"]
    #HTTP POST request
    if request.method == "POST":
        symbol_to_sell = request.form.get("symbol")
        shares = (request.form.get("shares"))

        if(not shares.isnumeric()):
            return apology("Please input a positive integer",400)
        else:
            shares = float(shares)
            if(shares <= 0):
                return apology("Please input a positive integer",400)

        company = db.execute("SELECT * FROM purchases WHERE symbol=? AND id = ?",symbol_to_sell,user_id)[0]
        current_comp_price = lookup(symbol_to_sell)['price']
        cash = db.execute("SELECT cash FROM users WHERE id=?",user_id)[0]['cash']
        print(cash)
        if(int(shares) > company['shares'] ):


           return apology("Too many shares",400)
        if(int(shares) == company['shares']):


            cash += float(company['shares']) * current_comp_price
            db.execute("UPDATE users SET cash=? WHERE id=?",cash,user_id)
            db.execute("DELETE FROM purchases WHERE id=? AND symbol=?",user_id,symbol_to_sell)
            return redirect("/")


        print("fat")
        new_shares = int(company['shares']) - int(shares)
        new_total = float(company['total']) - (float(shares) * current_comp_price)
        cash += float(shares) * current_comp_price
        db.execute("UPDATE users SET cash=? WHERE id=?",cash,user_id)
        db.execute("UPDATE purchases SET shares=?,total=? WHERE id=? ",new_shares,new_total,user_id)

        db.execute("INSERT INTO history (price,symbol,shares,id) VALUES(?,?,?,?)",current_comp_price,symbol_to_sell,shares * -1,
        session['user_id'])
        return redirect("/")

    else:


        symbol_list = db.execute("SELECT symbol FROM purchases WHERE id=?",user_id)

        return render_template("sell.html",symbols=symbol_list)
