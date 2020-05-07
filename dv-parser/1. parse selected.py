#/usr/bin/python3

""" Parse all html source files in data subdir into csv. """

from bs4 import BeautifulSoup
import csv
from unicodedata import normalize
from pprint import pprint
import locale
from glob import glob
import os
import re


# We have numbers in US style
locale.setlocale( locale.LC_ALL, "en_US.UTF-8")


def parse_row(row):
        """ Parses single row of an html table. """

        line = normalize("NFKD", row.get_text())
        countries = re.findall(r"[a-zA-Z\-][a-zA-Z\-, ’.&]+[a-zA-Z]", line)
        people = re.findall(r"\d[\d,]*", line)
        line = zip((c.title() for c in countries),  (locale.atoi(p) for p in people))
        return list(line)


def parse_html_file(f, nf):
    """ Parses single html file. """
 
    soup = BeautifulSoup(f, "html.parser")

    csvwriter = csv.writer(nf)

    for tbl in soup.find_all('table'):
        table = []
        for tr in tbl.find_all('tr'):
            if len(tr.find_all('td')) > 1:
                table.append(parse_row(tr))
        for i in range(3):
            for row in table:
                try:
                    csvwriter.writerow(row[i])
                except IndexError:
                    continue


os.chdir("data sources")
files = glob("*.html")
for name in files:
    print(name, " => ", new_name := name.replace("html", "csv"))
    f = open(name, encoding="utf-8")
    nf = open(new_name, "w", newline="")
    parse_html_file(f, nf)
