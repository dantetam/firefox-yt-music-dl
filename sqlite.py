import json
import subprocess
import os
import urllib.request
import re
from pathlib import Path
import sqlite3

from base import *


chosenHistoryFileName = "./history/places.sqlite"
outputDir = "./output/"


def main():
    downloadLimit = 100

    # Create a SQL connection to our SQLite database
    con = sqlite3.connect(chosenHistoryFileName)

    cur = con.cursor()

    queryResultsLen = 0
    # The result of a "cursor.execute" can be iterated over by row
    for row in cur.execute("SELECT * FROM moz_places WHERE visit_count >= 5 AND url LIKE '%youtube.com%';"):
        queryResultsLen = queryResultsLen + 1
        stringRow = [str(item) for item in row]
        print(";".join(stringRow).encode("utf-8"))
    print("Length of results from history database query: " + str(queryResultsLen), flush=True)


    path, dirs, files = next(os.walk(outputDir))
    file_count = len(files)
    print("Current number of downloaded music files: " + str(file_count), flush=True)


    # Be sure to close the connection
    con.close()

    print("History downloads complete", flush=True)
