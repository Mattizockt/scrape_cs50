import sqlite3
from flask import Flask, render_template, request, Blueprint, session
from scrape import apology
from jinja2 import Template

# initialize Blueprint
results = Blueprint(
    "resultation", __name__, static_folder="static", template_folder="templates"
)

# solltest überprüfen von welcheer seite results gescrapet werden (new hot usw.)
# show complete table
@results.route("/results", methods=["POST"])
def main():
    if request.method == "POST":

        conn = sqlite3.connect("reddit.db")
        c = conn.cursor()

        # what was the original cell
        operation = request.form.get("modus")
        requested_data = c.execute(session[operation])

        # gives back titloes for column
        titles = what_table_titles(operation)
        return render_template("cells.html", value=requested_data, titles=titles)
        # submit-button auf specs.html reagiert nicht auf klick


def what_table_titles(operation):
    if operation == "modus_titles":
        return ["Words", "Occurences"]
    elif operation == "modus_votes":
        return ["Votes", "Author", "Title"]
    elif operation == "modus_labels":
        return ["Label", "Occurences"]
    elif operation == "modus_weekdays":
        return ["Weekday (1-24, GMT+2)", "Occurences"]
    elif operation == "modus_hours":
        return ["Hour (1-24, GMT+2)", "[Occurences]"]
    elif operation == "modus_authors":
        return ["Author", "Amount of Posts"]
    elif operation == "modus_comments":
        return ["Comments", "Title", "Author"]


if __name__ == "__main__":
    app.run(debug=True)
