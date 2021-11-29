# from os import set_inheritable
import sqlite3
import re

from flask import Flask, flash, jsonify, redirect, request, render_template, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import redirect

from helpers import login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded (not sure that I actually need this line)
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
def index():
    return redirect("/lobbies")


@app.route("/register", methods=["GET", "POST"])
def register():    
    """Register user"""

    # create "connection" object that represents db; https://docs.python.org/3/library/sqlite3.html
    con = sqlite3.connect('teammaker.db')
    # create "cursor" object
    cur = con.cursor()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        login = request.form.get("login")
        password = request.form.get("password")
        repeat_password = request.form.get("repeat_password")
        username = request.form.get("username")

        # regex should take care of this (EXCEPT password repeat):
        # # Ensure username was submitted
        # if not username:
        #     return "must provide username"
        # # Ensure password was submitted
        # elif not password:
        #     return "must provide password"
        # elif password != repeat_password:
        #     return "'Password and 'Repeat password' do not match"

        # FROM THE PAST: It's important to insert both username and hash at the same time. Otherwise get SQL error that hash can't be NULL, and there may be several rows instead of one.
        
        # todo reallocate code to a bunch of NOT nested ifs
        # consider using "flask-wtf" for input check, watch https://youtu.be/UIJKdCIEXUQ
        # check login with regex: only allowed symbols, at least 4 of them, maximum 20 symbols
        if re.fullmatch(r'[A-Za-z0-9@#$%^&+=]{4,20}', login):
            # check that login is free
            # .execute - method that executes the query and modifies the "cursor" object (?)
            cur.execute("SELECT * FROM users WHERE login = :login", {"login": login})  # same as: (...login = ?", (login,)) - yep, comma is nesessary 
            # .fetchall returns a list, result of .execute
            lst = cur.fetchall()
            # print("MYDEBUG. lst (login) =", lst)
            if lst == []:
                # check password with regex: only allowed symbols, at least 4 of them, maximum 20 symbols
                if re.fullmatch(r'[A-Za-z0-9@#$%^&+=]{4,20}', password):
                    # confirm password and generate hash
                    if password == repeat_password:
                        password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
                    else:
                        return "Password and repeated password do not match"
                    # check username with regex: only allowed symbols, at least 2 of them, maximum 20 symbols
                    if re.fullmatch(r'[A-Za-z0-9@#$%^&+=]{2,20}', username):
                        # check that username is free
                        cur.execute("SELECT * FROM users WHERE username = ?", (username,))  # same as: (... username = :foo", {"foo": username}) ; https://docs.python.org/3/library/sqlite3.html
                        # .fetchall returns a list, result of .execute
                        lst = cur.fetchall()
                        # print("MYDEBUG. lst (username) =", lst)
                        if lst == []:
                            # create a row in database
                            cur.execute("INSERT INTO users (login, password_hash, username) VALUES (?, ?, ?)", (login, password_hash, username))
                            con.commit()
                        else:
                            return "Username already exists"
                    else:
                        return "Username should have 2-20 symbols; allowed symbols: numbers, latin letters (upper or lowercase), @#$%^&+="
                else:
                    return "Password should have 4-20 symbols; allowed symbols: numbers, latin letters (upper or lowercase), @#$%^&+="
            else:
                return "Login already exists"
        else:
            return "Login should have 4-20 symbols; allowed symbols: numbers, latin letters (upper or lowercase), @#$%^&+="

        # close the connection after login, password and username are saved in db
        # maybe too early ???
        # also, could use "with foo as bar:"
        con.close()

        return redirect("/")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        con.close()
        return render_template("/register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # create "connection" object that represents db; https://docs.python.org/3/library/sqlite3.html
    con = sqlite3.connect('teammaker.db')
    # create "cursor" object
    cur = con.cursor()

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return "must provide username"

        # Ensure password was submitted
        elif not request.form.get("password"):
            return "must provide password"

        # Query database for username
        search_for_username = cur.execute("SELECT * FROM users WHERE username = :username", {"username" : request.form.get("username")}).fetchall()
        # print("MYDEBUG", search_for_username)

        # Ensure username exists and password is correct
        # search_for_username returns a list of tuples [(id, 'username', 'password_hash', 'login')]; check_password_hash returns True or False (password_hash, provided password)
        if not search_for_username or not check_password_hash(search_for_username[0][2], request.form.get("password")):
            return "invalid username and/or password"

        #TEST STRINGS
        # if not search_for_username:
        #     return "invalid username"
        # if not check_password_hash(search_for_username[0][2], request.form.get("password")):
        #     return "wrong password"

        # Remember which user has logged in
        # search_for_username returns a list of tuples [(id, 'username', 'password_hash', 'login')]; so [0][0] is user's id from database table "users"
        session["user_id"] = search_for_username[0][0]

        # Show message
        flash('You were successfully logged in')

        # Redirect user to home page
        con.close()
        return redirect("/")
        
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        con.close()
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    con = sqlite3.connect('teammaker.db')
    cur = con.cursor()
    user_id = session["user_id"]
    
    cur.execute("DELETE FROM lobbies WHERE user_id = :user_id", {"user_id" : user_id})
    con.commit()
    con.close()

    # Clear any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/lobbies", methods=["GET", "POST"])
def lobbies():
    """Shows lobbies and allows to join them"""
    
    # User reached route via POST; allows user to join the lobby
    if request.method == "POST":
        # if anytime I would want to allow the user to join only one lobby - change "lobbies" table in DB - make "user_id" UNIQUE

        # ???do i need it here??? create "connection" object that represents db; https://docs.python.org/3/library/sqlite3.html
        con = sqlite3.connect('teammaker.db')
        # ???do i need it here??? create "cursor" object
        cur = con.cursor()

        try:
            user_id = session["user_id"]
            # ??? how do i get game_id from submit? <input type="hidden" id="game_id" name="game_id" value="1"> ?
        except KeyError:
            flash("In order to join lobby you must be logged in")  # for some reason this line doesn't work
            return redirect("/login")

        #game_id = request.form.get("game_id")
        game = request.form.get("game")

        #lobby_name = request.form.get("lobby_name")  # ??? what does a button return ???

        # user is already in the lobby if inquiry returns anything except an empty list;
        # here we take user's id and game's name, then check if both are already in the lobby table at the same line
        if cur.execute("""
                        SELECT * FROM lobbies
                        WHERE user_id = :user_id AND game_id = (SELECT games.id FROM games WHERE games.game = :game)
                        """, {"user_id" : user_id, "game" : game }).fetchall() != []:
                        flash("You are already in the lobby")
        else:
            join_lobby = cur.execute("""
                                    INSERT INTO lobbies (user_id, game_id)
                                    VALUES (:user_id, (SELECT id FROM games WHERE game = :game))
                                    """, {"user_id" : user_id, "game" : game})
            con.commit()
        
        # # gets usernames in specific game lobby
        # usernames = cur.execute("SELECT username FROM users WHERE id IN (SELECT id FROM lobbies WHERE lobbies.user_id = users.id AND game_id = :game_id)", {"game_id" : game_id})
        con.close()
        return redirect("/lobbies")

    # User reached route via GET (as by clicking a link or via redirect); show all lobbies and users in them
    else:
        return render_template("/lobbies.html")


@app.route("/leave_lobby", methods=["POST"])
@login_required
def leave_lobby():
    """Leave one particular lobby"""

    con = sqlite3.connect('teammaker.db')
    user_id = session["user_id"]
    # get name of the game from html and convert it to game_id from db;
    # fetchall() returns list of tuples [(id,)]
    game_id = con.execute("SELECT id FROM games WHERE game = :game", {"game" : request.form.get("game")}).fetchall()[0][0]

    # if everything is fine code in "try" is executed and transaction is commited, if something goes wrong "with" rolls db back; "finally" closes db and is executed either way
    try:
        # connection as a context manager automatically calls con.commit() if transaction was succesfull
        with con:
            con.execute("DELETE FROM lobbies WHERE user_id = :user_id AND game_id = :game_id", {"user_id" : user_id, "game_id" : game_id})
            flash(f"You left the lobby {request.form.get('game')}")  # could be used for sql injection (returning malicious code in "value" from lobbies.html)?
            # can't put "con.close()" here, because "with" still uses the db
            return redirect("/lobbies")
    finally:
        con.close()
        

@app.route("/leave_all_lobbies", methods=["POST"])
@login_required
def leave_all_lobbies():
    """Leave all lobbies"""

    user_id = session["user_id"]
    con = sqlite3.connect('teammaker.db')
    
    # if everything is fine code in "try" is executed and transaction is commited, if something goes wrong "with" rolls db back; "finally" closes db and is executed either way
    try:
        # connection as a context manager automatically calls con.commit() if transaction was succesfull
        with con:
            con.execute("DELETE FROM lobbies WHERE user_id = :user_id", {"user_id" : user_id})
            flash("You left all lobbies")
            return redirect("/lobbies")
    finally:
        con.close()


# def lobby_updater():
#     """Creates json for javascript to automatically update lobbies"""

#     # create "connection" object that represents db; https://docs.python.org/3/library/sqlite3.html
#     con = sqlite3.connect('teammaker.db')
#     # create "cursor" object
#     cur = con.cursor()

#     # .fetchall returns a list of tuples, result of .execute; cursor object can also be iterated
#     all_lobbies_and_users = cur.execute("""
#                                         SELECT games.game, users.username
#                                         FROM games
#                                         JOIN lobbies ON games.id = lobbies.game_id
#                                         JOIN users ON users.id = lobbies.user_id
#                                         """).fetchall()

#     # list of all games/lobbies (need that to show empty lobbies)
#     raw_games_names = cur.execute("SELECT game FROM games").fetchall() #[(ow), (sc), (ns)]
#     games_names = []
#     foo = [games_names.append(key[0]) for key in raw_games_names]

#     # dictionary with lists of all users sorted to corresponding games {game1 : [user1, user2], game2 : [user3, user4]}
#     # probably there is an easier way using jsonify
#     users_in_lobbies_dict = {}
#     for row in all_lobbies_and_users:
#         if row[0] not in users_in_lobbies_dict.keys():
#             users_in_lobbies_dict[row[0]] = [row[1]]
#         else:
#             users_in_lobbies_dict[row[0]].append(row[1])

#     # when should I con.close() ??? "with ... as ..." only commits the cursor, db should still be closed manually
#     con.close()
#     return jsonify(users_in_lobbies_dict = users_in_lobbies_dict, games_names = games_names)


@app.route("/lobbies_names", methods=["GET"])
def lobbies_names():
    """Creates json for javascript with only names of lobbies (empty encluded)"""
    
    # create "connection" object that represents db; https://docs.python.org/3/library/sqlite3.html
    con = sqlite3.connect('teammaker.db')
    # create "cursor" object
    cur = con.cursor()

    # list of all games/lobbies (need that to show empty lobbies)
    raw_lobbys_names = cur.execute("SELECT game FROM games").fetchall() #[(ow), (sc), (ns)]
    lobbies_names = []
    foo = [lobbies_names.append(key[0]) for key in raw_lobbys_names]

    # when should I con.close() ??? "with ... as ..." only commits the cursor, db should still be closed manually
    con.close()
    return jsonify(lobbies_names = lobbies_names)


@app.route("/lobbies_users", methods=["GET"])
def lobbies_users():
    """Creates json for javascript with users in lobbies {game1 : [user1, user2], game2 : [user3, user4]}"""

    # create "connection" object that represents db; https://docs.python.org/3/library/sqlite3.html
    con = sqlite3.connect('teammaker.db')
    # create "cursor" object
    cur = con.cursor()

    # .fetchall returns a list of tuples, result of .execute; cursor object can also be iterated
    all_lobbies_and_users = cur.execute("""
                                        SELECT games.game, users.username
                                        FROM games
                                        JOIN lobbies ON games.id = lobbies.game_id
                                        JOIN users ON users.id = lobbies.user_id
                                        """).fetchall()

    # dictionary with lists of all users sorted to corresponding games {game1 : [user1, user2], game2 : [user3, user4]}
    # probably there is an easier way using jsonify
    lobbies_users = {}
    for row in all_lobbies_and_users:
        if row[0] not in lobbies_users.keys():
            lobbies_users[row[0]] = [row[1]]
        else:
            lobbies_users[row[0]].append(row[1])


    # list with empty lobbies only
    raw_empty_lobbies = cur.execute("""
                                SELECT game FROM games WHERE id NOT IN (SELECT game_id FROM lobbies);
                                """).fetchall()

    empty_lobbies = []
    for tuple in raw_empty_lobbies:
        empty_lobbies.append(tuple[0])

    # same but using List Comprehension
    # other_empty_lobbies = []
    # [other_empty_lobbies.append(tuple[0]) for tuple in raw_empty_lobbies]

    # when should I con.close() ??? "with ... as ..." only commits the cursor, db should still be closed manually
    con.close()
    return jsonify(lobbies_users = lobbies_users, empty_lobbies = empty_lobbies)


@app.route("/profile", methods=["GET"])
@login_required
def profile():    
    """Shows profile page"""
    if request.method == "GET":
        # create "connection" object that represents db; https://docs.python.org/3/library/sqlite3.html
        con = sqlite3.connect('teammaker.db')
        # create "cursor" object
        cur = con.cursor()

        # session is kinda like a dictionary... can't find exact info in docs right now, anyways, it stores user_id when user is logged in
        user_id = session["user_id"]
        # cur.execute(...) returns a list of tuples [('username',]; so [0][0] is user's username from database table "users"
        username = cur.execute("SELECT username FROM users WHERE id = :id", {"id" : user_id}).fetchall()[0][0]

        con.close()
        return render_template("profile.html", username = username)


@app.route("/change_password", methods=["POST"])
@login_required
def change_password():
    """Changes password"""
    # 1 check that new_password has necessary length and symbols
    # 2 check that new_password and confirmation are same
    # 3 check that old password is correct - don't know how to do this, cashes are obviously different, thanks to salt
    # 4 change password 

    con = sqlite3.connect('teammaker.db')
    cur = con.cursor()

    new_password = request.form.get("new_password")
    confirmation = request.form.get("confirmation")

    # check new_password with regex: only allowed symbols, at least 4 of them, maximum 20 symbols
    if not re.fullmatch(r'[A-Za-z0-9@#$%^&+=]{4,20}', new_password):
        return ("Password must have 4-20 symbols, allowed symbols: decimals, latin letters (upper or lowercase), @#$%^&+=")
    else:
        if new_password != confirmation:
            return ("New password and confirmation do not match. Please try again.")
        else:
            new_hash = generate_password_hash(new_password, method='pbkdf2:sha256', salt_length=16)
            cur.execute("UPDATE users SET password_hash = :password_hash WHERE id = :id", {"password_hash" : new_hash, "id" : session["user_id"]})
            con.commit()
            con.close()            
            flash("Password has been changed succesfully")
            return redirect("/profile")

        
@app.route("/user_info", methods=["GET"])
def user_info():
    try:
        user_id = session["user_id"]
        print(user_id)
        
        con = sqlite3.connect('teammaker.db')
        cur = con.cursor()
        
        username = cur.execute("SELECT username FROM users WHERE id = :id", {"id" : user_id}).fetchall()[0][0]
        # print(username)

        con.close()

        return jsonify(user_id = user_id, username = username)
    except KeyError:
        # print("no user_id")
        return jsonify("no user_id")