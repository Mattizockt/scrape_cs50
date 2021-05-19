from flask import Flask, render_template, request
from scrape import scrape
from specs import specs
from results import results

app = Flask(__name__)
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = "super secret key"
app.register_blueprint(scrape, url_prefix="")
app.register_blueprint(specs, url_prefix="")
app.register_blueprint(results, url_prefix="")

# to access loop extensions(break)
# app.jinja_env.add_extension("jinja2.ext.loopcontrols")

# mainpage
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/specs")
def spec():
    return render_template("specs.html")


@app.after_request
def add_header(response):
    response.cache_control.max_age = 300
    return response


if __name__ == "__main__":
    app.run(debug=True)
