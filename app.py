import sqlite3
# from sqlalchemy import create_engine, text

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded (not sure that I actually need this line)
app.config["TEMPLATES_AUTO_RELOAD"] = True

# create "connection" object that represents db; https://docs.python.org/3/library/sqlite3.html
con = sqlite3.connect('teammaker.db')

# create "cursor" object
cur = con.cursor()

# reundant code. I decided to use standard library sqlie3 for now
# # create engine for SQLAlchemy (https://docs.sqlalchemy.org/en/14/tutorial/engine.html#tutorial-engine)
# engine = create_engine("sqlite://teammaker.db", echo=True, future=True)

# # with engine.connect() as conn:
# #     result = conn.execute(text(""))

# just use sqlite3 lib from stdlib???