#/usr/bin/python3

""" Parse all pdf source files in data subdir into csv. """

import os
import tabula
import json
from glob import glob
import csv

def parse_pdf_file(f, nf):
    csvwriter = csv.writer(nf)

    for x in f:
        for i in x["data"]:
            line = []
            if i[0]["text"] == '': continue
            if 'Foreign State' in i[0]["text"]: continue
            if 'Total' in i[0]["text"]: continue
            if 'TOTAL' in i[0]["text"]: continue
            if '' == i[1]["text"]: continue
            for j in i:
                '''len(j["text"]) < 1 or''' 
                line.append(j["text"])
            csvwriter.writerow(line)


os.chdir('data sources')
files = glob("*.pdf")
for name in files:
    if "FY" not in name: continue
    print(name, " => ", new_name := name.replace("pdf", "csv"))
    f = tabula.read_pdf(name, pages="all", output_format="json", silent=True)
    nf = open(new_name, "w", newline="")
    parse_pdf_file(f, nf)