import sqlite3
from flask import Flask, render_template, request, Blueprint, session

# initialize Blueprint
specs = Blueprint(
    "specifications", __name__, static_folder="static", template_folder="templates"
)


@specs.route("/specs", methods=["GET", "POST"])
def main():
    if request.method == "POST":

        conn = sqlite3.connect("reddit.db")
        c = conn.cursor()

        # take data from default or new table
        if session["standard"] == True:
            table = "results"
        else:
            table = "standard_results"

        objection = Mailbox(c, table, request.form.get("calc_all"))
        final_selection = append_list(objection)

        return render_template("results.html", result=final_selection)

        conn.close()
    else:
        return render_template("specs.html")


# checks if input field is checked
def is_null(value):
    checkbox = request.form.get(value)
    if checkbox == None:
        return "Not Checked"
    else:
        return checkbox


# packs variable into array
class Mailbox:
    def __init__(self, c, table, calc_all):
        self.table = table
        self.c = c
        self.calc_all = calc_all

    def mail(self, query, requested_cell):

        # add limit and check if cell ist checled
        temp = query.format(self.table) + " LIMIT 50"
        checked_requested_cell = is_null(requested_cell)

        # if current cell selected, do this
        if self.calc_all == "1" or checked_requested_cell == "True":

            # string in session to access it later
            session[requested_cell] = temp
            return self.c.execute(temp).fetchall()[0]

        # is checkbox emty?

        # if checked_requested_cell == "True":

        #     # storing in session to access it later
        #     session[requested_cell] = temp

        #     return self.c.execute(temp).fetchall()

        else:
            return "-"


# gives back an array with all values
def append_list(objection):

    final_selection = []

    # total ids
    final_selection.append(objection.mail("SELECT COUNT(id) FROM {}", "total_ids"))
    # total votes
    final_selection.append(objection.mail("SELECT SUM(votes) FROM {}", "total_votes"))
    # total labels
    final_selection.append(
        objection.mail("SELECT COUNT(DISTINCT labels) FROM {}", "total_labels")
    )

    # total authors
    final_selection.append(
        objection.mail("SELECT COUNT(DISTINCT authors) FROM {}", "total_authors")
    )
    # total comments
    final_selection.append(
        objection.mail("SELECT SUM(comments) FROM {}", "total_comments")
    )

    #
    #

    # average votes
    final_selection.append(
        objection.mail("SELECT ROUND(AVG(votes) ,2) FROM {}", "average_votes")
    )
    # average comments
    final_selection.append(
        objection.mail("SELECT ROUND(AVG(comments) ,2) FROM {}", "average_comments")
    )

    #
    #

    # modus word in title
    final_selection.append(
        objection.mail(
            """with recursive cte as (
            select null as word, titles || ' ' as rest, 0 as lev
            from {}
            union all
            select substr(rest, 1, instr(rest, ' ') - 1) as word, 
                    substr(rest, instr(rest, ' ') + 1) rest,
                    lev + 1
            from cte
            where lev < 5 and rest like '% %'
            )
        select word, count(*)
        from cte
        where word is not null
        group by word
        order by count(*) desc
        """,
            "modus_titles",
        )
    )
    # modus votes
    final_selection.append(
        objection.mail(
            "SELECT votes,authors,titles FROM {} ORDER BY votes DESC", "modus_votes"
        )
    )
    # modus labels
    final_selection.append(
        objection.mail(
            "SELECT labels, COUNT(labels) FROM {} GROUP BY labels ORDER BY COUNT(*) DESC",
            "modus_labels",
        )
    )
    # modus weekdays
    final_selection.append(
        objection.mail(
            "SELECT weekdays, COUNT(weekdays) FROM {} GROUP BY weekdays ORDER BY COUNT(*) DESC",
            "modus_weekdays",
        )
    )

    # modus_hours
    final_selection.append(
        objection.mail(
            "SELECT SUBSTR(hours, 1, 2) AS hello, COUNT(*) FROM {} GROUP BY hello ORDER BY COUNT(*) DESC",
            "modus_hours",
        )
    )

    # modus posts
    final_selection.append(
        objection.mail(
            "SELECT authors, COUNT(*) FROM {} GROUP BY authors ORDER BY COUNT(*) DESC",
            "modus_authors",
        )
    )

    # modus comments
    final_selection.append(
        objection.mail(
            "SELECT comments, titles, authors FROM standard_results ORDER BY comments DESC",
            "modus_comments",
        )
    )

    return final_selection


if __name__ == "__main__":
    app.run(debug=True)
