from flask import Flask, render_template
from blueprints import user_blueprint, account_blueprint

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SECRET_KEY"] = '5d123d21152d482bb4a1605f5178d1a5'


@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.register_blueprint(user_blueprint, url_prefix='/user')
    app.register_blueprint(account_blueprint, url_prefix='/account')
    app.run(host="0.0.0.0", port=15001, debug=True)
