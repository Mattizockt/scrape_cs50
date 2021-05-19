import time
import sys
import os
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
import sqlite3
from flask import Flask, render_template, request, Blueprint, redirect, session
from datetime import datetime
import calendar


scrape = Blueprint(
    "scraping", __name__, static_folder="static", template_folder="templates"
)


@scrape.route("/", methods=["GET", "POST"])
def main():
    if request.method == "POST":

        # use premade table?
        if request.form.get("standart_table") == "1":
            session["standard"] = False
            return redirect("/specs")

        # make table
        session["standard"] = True

        # get rid of old table
        delete_old_table()

        # ask user to scrape how many pages
        if request.form.get("pages").isdigit() == False:
            return apology("Only integers")
        number_of_results = int(request.form.get("pages"))

        page_counter = 0

        # getting driver and installing old reddit driver (makes it easier to scrape)
        chrome_options = Options()
        chrome_options.add_extension(os.path.abspath(r"crx_files\reddit_old.crx"))

        driver = webdriver.Chrome("./chromedriver", options=chrome_options)
        driver.get("https://www.reddit.com/r/cs50/new/")

        # looping through every page while finding results
        while True:
            wait = WebDriverWait(driver, 20)

            # keep track of how many pages were scraped
            page_counter += 1

            # get diffrent attributes
            titles, votes, labels, publishing_dates, author, comments = scrape_page(
                driver
            )
            write_to_db(titles, votes, labels, publishing_dates, author, comments)

            # stop when amount of scraped pages equals users desire
            if page_counter == number_of_results:
                print("Scraped", number_of_results, "pages.")
                driver.quit()
                return redirect("/specs")

            # go to next page
            does_button_exist = go_to_next_page(driver, page_counter)
            if does_button_exist == False:
                driver.quit()
                return redirect("/specs")
    else:
        return render_template("index.html")


# asks user how many pages he wants to scrape
# CHANGE COMMA INPUT
def number_results(request):
    pages = request.form.get("pages")
    if pages.isdigit() == True:
        return int(pages)


# collects data from one page
def scrape_page(driver):
    standart_path = r"//div[contains(@class, 'linkflair') and @data-author]"

    titles = driver.find_elements_by_xpath(standart_path + "//a[@tabindex='1']")
    votes = driver.find_elements_by_xpath(
        standart_path + "//div[@class='score unvoted']"
    )
    labels = driver.find_elements_by_xpath(
        standart_path + "//span[@class = 'linkflairlabel ']"
    )
    publishing_dates = driver.find_elements_by_xpath(standart_path + "//time")
    authors = driver.find_elements_by_xpath(
        standart_path + "//a[contains(@href, 'user')]"
    )
    comments = driver.find_elements_by_xpath(
        standart_path + "//a[@data-event-action='comments']"
    )

    return (titles, votes, labels, publishing_dates, authors, comments)


# copied from cs50
def apology(message, code=400):
    return render_template("apology.html", top=code, bottom=message)


# writes data to database
def write_to_db(titles, votes, labels, publishing_dates, authors, comments):

    conn = sqlite3.connect("reddit.db")
    c = conn.cursor()

    c.execute(
        """CREATE TABLE IF NOT EXISTS 
        results (
            id INTEGER NOT NULL PRIMARY KEY,
            titles TEXT,
            votes INT, 
            labels TEXT,    
            weekdays TEXT,
            hours TEXT,
            authors TEXT, 
            comments INT
            )
        """
    )
    conn.commit()

    # create object to process certain arguments
    processor = Processor()
    for i, item in enumerate(titles):

        # calculating time. time[0] gives date, time[1] gives hour, minute
        time = processor.process_time(publishing_dates[i].get_attribute("datetime"))

        # calculatess (string name) by passing in the date
        weekdays = calendar.day_name[datetime.strptime(time[0], "%Y-%m-%d").weekday()]

        c.execute(
            """INSERT INTO 
                results (
                    titles, votes, labels, weekdays, hours, authors, comments
                    )
                VALUES (
                    ?,?,?,?,?,?,?
                    )
                """,
            (
                item.text,
                processor.process_votes(votes[i].text),
                labels[i].text,
                weekdays,
                time[1],
                authors[i].text,
                processor.process_comments(comments[i].text[0]),
            ),
        )
        conn.commit()

    conn.close()


def delete_old_table():
    conn = sqlite3.connect("reddit.db")
    c = conn.cursor()
    c.execute(
        """DELETE FROM results
            """
    )
    conn.commit()


# process attributes to fit into sql database
class Processor:
    def process_votes(self, votes):
        if votes == "•":
            return "0" + "\n"
        else:
            return votes + "\n"

    def process_comments(self, comments):
        if comments == "k":
            return "0" + "\n"
        else:
            return comments + "\n"

    def process_time(self, time):
        def split2(time):
            return time[:19]

        time = split2(time).split("T")
        return time


# click next page button
def go_to_next_page(driver, page_counter):
    elements = driver.find_elements_by_xpath("//span[@class='next-button']")
    try:
        elements[0].click()
        print("successfully skipped to next page")
        return True
    except IndexError:
        print(
            "your are at the end of the subreddit. \n There were only",
            page_counter,
            "pages.",
        )
        return False


if __name__ == "__main__":
    app.run(debug=True)