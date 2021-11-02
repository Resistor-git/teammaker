from os import set_inheritable
import sqlite3
import re

from flask import Flask, redirect, request, render_template, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import redirect

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
    return redirect("/register")


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
            print("MYDEBUG. lst (login) =", lst)
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
                        print("MYDEBUG. lst (username) =", lst)
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

        return "todo /mainpage"
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("/register.html")


@app.route("/lobbies", methods=["GET", "POST"])
def lobbies():
    """Shows lobbies and allows to join them"""
    # TODO
    # User reached route via POST; submits which lobby be wants to join
    if request.method == "POST":
        # create "connection" object that represents db; https://docs.python.org/3/library/sqlite3.html
        con = sqlite3.connect('teammaker.db')
        # create "cursor" object
        cur = con.cursor()

        user_id = session["user_id"]
        # ??? how do i get game_id from submit? <input type="hidden" id="game_id" name="game_id" value="1"> ?
        game_id = request.form.get("game_id")
        #game_id_querie  = cur.execute("SELECT game FROM games WHERE lobbies.id = :id", {"id": ???})  
        #lst = cur.fetchall()  # ???
        lobby_name = request.form.get("lobby_name")  # ??? what does a button return ???
        join_lobby = cur.execute("INSERT INTO lobbies (user_id, game_id) VALUES (?, ?)", (user_id, game_id))

        # gets usernames in specific game lobby
        usernames = cur.execute("SELECT username FROM users WHERE id IN (SELECT id FROM lobbies WHERE lobbies.user_id = users.id AND game_id = :game_id)", {"game_id" : game_id})

    # User reached route via GET (as by clicking a link or via redirect); show him relevant users from the databese
    else:
        # create "connection" object that represents db; https://docs.python.org/3/library/sqlite3.html
        con = sqlite3.connect('teammaker.db')
        # create "cursor" object
        cur = con.cursor()

        # test strings
        # lobby_id = cur.execute("SELECT id FROM lobbies")
        # lobby_users = cur.execute("SELECT user_id FROM lobbies")
        # print("MYDEBUG lobby_id type -", type(lobby_id))

        # .fetchall returns a list, result of .execute; cursor object can also be iterated
        all_lobbies_and_users = cur.execute("""SELECT games.game, users.username
                            FROM games
                            JOIN lobbies ON games.id = lobbies.game_id
                            JOIN users ON users.id = lobbies.user_id
                            """)#.fetchall()

        # whecn should I con.close() ??? probably should just use "with ... as ..."
        return render_template("/lobbies.html", all_lobbies_and_users = all_lobbies_and_users)



# def join_lobby:
#     lobby_lst = SELECT foo
#     return lobby_lst