# Teammaker
#### https://resistor.pythonanywhere.com/
#### Video Demo:  <https://youtu.be/yO7J-L_XJ3I>
Teammaker is a service created to help people gather to play games.

The idea is simple: if you want to find a teammate or opponent you visit the site, check who is in lobbies and join.

Teammaker does not provide any additional services like chat, friendlist, game launch directly from the page or whatsoever.
## Structure (tree)
    • Main page (lobbies)
    • Profile
    • Log in
    • Register
Each page has a navigation panel at the top. Click on 'Teammaker' will lead you to the main page, 'Profile' leads to profile page, 'Log in' redirects to respective form. 'Log out' stops session for the current user. 'Register' leads to registration form. Depending on current status user sees only one the last three links, either 'log in' or 'log out' or 'register'.
Main page consists of several lobbies, one for each game. User can join or leave any of them. User can join several lobbies at the same time. Only restriction is authorisation, if you are not logged in and try to join lobby, you will be redirected to the login form. However, authorisation is not necessary if you just checking the main page. Lists of players in lobbies are updated every several seconds.

Profile page shows name of the current user and lets you change the password.

Login page consists of two text fields: login and password. If both of them are correct, then user is redirected to main page and may join or leave lobbies. User also gains access to profile page. If login or password is wrong, user you will see an error message.

Register page has several text fids. 'Login' is the login you will use to authorise, noone will see it. 'Password' is also for authorisation, this field and 'Confirmation' must be the same. 'Username' is the nickname everyone will see when you join a lobby.
## The code
Server side (backend) is written on Flask. Pages are generated using Jinja (as recommended by Flask documentation), javascript, html and css. Database SQLite.

For more advanced information check corresponding documentation:

https://flask.palletsprojects.com/en/2.0.x/

https://jinja.palletsprojects.com/en/3.0.x/

https://werkzeug.palletsprojects.com/en/2.0.x/

https://developer.mozilla.org/ru/docs/Web/

https://www.sqlite.org/index.html
### Files
Folder “static” contains static files: javascript, logos and CSS styles.

Folder “templates” contains html files with code in Jinja.

“app.py” - backend in Flask.

“helpers.py” - some additional functions simplifying the coding process.

“requirements.txt.” - libraries essential for site deployment.

“teammaker.db” - SQL database.
### The database
Database is represented by the “teammaker.db” file. It’s simple and relational, created using SQLite. Not much to say about it. Three tables: users, lobbies, games.

You can see it’s high quality artistic representation in file “dbpic.png”. If you want to databases' contents locally I recommend “DB Browser for SQLite”.

#### app.py
The basics of the whole site. Contains functions each of which provides data for frontend.

Imports:

    • sqlite3 - standard python library for working with sql, chose it because it looked simpler than SQLalchemy and at the same time gets job done;
    
    • re - standard python library for regular expressions, used to check that user’s input (logins, passwords…) meets the constraints, could use special plugins for Flask to do the same job but “re” looked like more straightforward and simple solution for my task;
    
    • Flask, flash, jsonify, redirect, request, render_template, session - Flask is just needed, flash is for the “alert” messages, redirect redirects to another page, request gets data from frontend, render_template renders a page based on a special template, session provides functional to authorise the user (basically to give id), for further info check Flask documentation;
    
    • tempfile - used to store necessary session info in temporary file (instead of signed cookies);
    
    • werkzeug.security - checks and generates password hashes, for security reasons;
    
    • werkzeug.utils - used to redirect user from one page to another;
    
    • helpers - .py file that has very important function login_required, it allows any function to proceed only if user has logged in;

Functions (app.py):

each function is called when user visits some address with corresponding request (get or post)

    • index() - redirects to main page, which is “/lobbies”, kinda “trash” function but does no harm, so I don’t touch it.
    
    • register() - registers new users. First you have to establish connection with the database. User will be prompted to fill text forms and register. Backend uses “request.form.get” command to get info from frontend. Then regular expression checks that username and password consist only from allowed symbols: latin letters, decimals, special symbols @#$%^&+= (dot is not allowed). Password and password confirmation should have same values. If everything is fine then a new record in database is created, it has login, username and hashed password. For hash purposes I use function `generate_password_hash` built in werkzeug library, pbkdf2/sha256.
    
    • login() - logs user in. User types his login and password, data is sent to server where it’s checked using an sql inquiry and special function `check_password_hash` from werkzeug. If information from user matches database then he is considered logged in and gets an ID, which is is identical to his ID in database. If user provided wrong info, an error message is shown.
    
    • logout() - logs user out and removes him from table ‘lobbies’ in database, so his nickname iis no longer shown as user in lobby. Database is changed using sql inquiry, ID is cleared by special Flask function `session.clear()`.
    
    • lobbies() - when the user clicks a button “join” or “leave” function asks database, and if the user is not already in the lobby let’s him in by creating new line in the “lobbies” table of the database. This function also initiates rendering of the “lobbies.html”, although all content is generated by other functions.
    
    • leave_all_lobbies() - pretty self explanatory. Deletes user from table “lobbies” if user clicked the corresponding button.
    
    • lobbies_names() - creates json for javascript with only names of lobbies. JS uses it to generate some parts of the page. See part of readme about “js_scripts.js”.
    
    • lobbies_users() - creates json for javascript with users in lobbies and empty lobbies. JS uses it to generate some parts of the page. See part of readme about “js_scripts.js”.
    
    • profile() - provides name of the current user and initiates rendering of the page “profile.html”
    
    • change_password() - allows the user to change password on the profile page. User is prompted to enter new password and to confirm it in adjacent form. If both of them are the same, then new password is checked by regular expression. If it meets the requirements then old password hash is replaced by new one. On a side note: originally I was going to also check that user knows the old password, but there is a problem - I don’t have the password in database, only the hash. And thanks to salt, I can’t compare hashes directly even if they were generated on the same basis. Of course, there are solutions for this problem, but I decided to abandon the idea of asking for old password. Moreover, it’s kinda redundant since user should be already logged in to enter the profile with password changing form.
    
    • user_info() - this function generates json with information about the current user: id and username. Javascript uses this info to create buttons. For example: if user joined the lobby, button “leave lobby” is created and button “join lobby” is removed.

#### js_scripts.js
File “js_scripts” is responsible for rendering and updating the main content on page “/lobbies”, such as lobbies with users in them and buttons to join or leave.

    • var user_info_variable - global variable (I know, it’s a bad practice), may be either “null” or a json object, for example { user_id: 5, username: "foo" }. Used by another function `create_buttons()`, if not null then button “leave_lobby” should be created.
    
    • lobbies_names() - creates titles for lobbies in a form of `<p>` elements, and these titles, in turn, serve as an anchor to which all other elements of lobbies are connected. Information about how these lobbies should be named is taken from the server in a from of json file, by calling `fetch(‘/lobbies_names’)`. Each `<p>` element has an id stripped of whitespaces.
    
    • lobbies_users() - takes response from server and draws a list of users in a lobby. In html terms it created `<ul>` after a corresponding <p> created  by `lobbies_names()`.
    
    • create_buttons() - creates buttons “join lobby”, “leave lobby”, “leave all lobbies” according to some conditions. If user is already in the lobby only “leave” will be displayed, otherwise only “join” exists.
    
    • test_buttons() - exists only for testing purposes. Allows to call functions manually by pressing buttons on the page. Was created due to a problem when because of asynchronous execution of the code the result was a pile of bugs and mess.
    
    • starter() - initiates rendering of the lobbies. Calls functions in a particular order and with some delay. Delay is necessary due to asynchronous execution of javascript, work of browser and latency between inquiries to the database. Function called only after the page is loaded, thanks to `window.addEventListener('load', starter)`.
    
    • updater() - constantly calls function `lobbies_users()` in order to update the list of users inside the lobbies. Which in its turn leads to creation or removal of buttons and etc. Called every several seconds (5 by default) by another anonymous function `setInterval(() => {updater()}, 5000)`.

### Appendix:

Working with database using sqlite3

For a comprehensive guide check https://docs.python.org/3/library/sqlite3.html. Simple version:

    1. Create 'connection' to the database con = sqlite3.connect('path_to_db').
    
    2. Create 'cursor' object cur = con.cursor().
    
    3. Execute sql inquiry cur.execute('SELECT foo FROM bar…').
    
    4. If the inquiry has changed the database - commit changes using con.commit.
    
    5. Close connection to the database con.close().
