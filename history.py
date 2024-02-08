import json
import subprocess
import os
import urllib.request
import re
from pathlib import Path
import sqlite3

from base import *

# sys.stdout = codecs.getwriter("utf8")(sys.stdout, 'xmlcharrefreplace')

chosenHistoryFileName = findFirefoxPath() + "places.sqlite"
# chosenHistoryFileName = "./history/places.sqlite"


def main():
    removeDupesAndSanitize("./output/")

    downloadLimit = 1000

    print("Attempting to read file: " + chosenHistoryFileName)

    # Create a SQL connection to our SQLite database
    con = sqlite3.connect(chosenHistoryFileName)

    cur = con.cursor()

    print("Executing sqlite query...")

    # The result of a "cursor.execute" can be iterated over by row
    for row in cur.execute("SELECT * FROM moz_places WHERE visit_count >= 5 AND url LIKE '%youtube.com%';"):
        print(str(downloadLimit) + " files left from history")
        #print(str(row).encode("utf-8"), flush=True)
        actuallyDownloadedFile = downloadMusic(row[1], removeExtraBitsTitle(row[2]))
        if actuallyDownloadedFile:
            downloadLimit = downloadLimit - 1
            if downloadLimit <= 0:
                break

    # Be sure to close the connection
    con.close()

    print("History downloads complete", flush=True)
