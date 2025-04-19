import json
import subprocess
import os
import glob
import urllib.request
import requests
import re
from pathlib import Path
import sys
import codecs
import sqlite3
import progressbar
import time

# sys.stdout = codecs.getwriter("iso-8859-1")(sys.stdout, 'xmlcharrefreplace')


# chosenBookmarkFileName = "./bookmarks/bookmarks-2022-06-22.json"
userDrivePath = "C:/Users/dante" #no slash at right end
ytExe = "yt-dlp-2025.exe"


def createFolderIfNonexistent(path):
    existingFile = Path(path)
    if not existingFile.is_dir():
        os.makedirs(path)


def findFirefoxPath():
    profilesPath = userDrivePath + "/AppData/Roaming/Mozilla/Firefox/Profiles/"
    profilesDir = os.path.abspath(profilesPath)
    profiles = os.listdir(profilesDir)
    if len(profiles) > 0:
        for profile in profiles:
            curProfilesPath = profilesPath + profile
            profileChildren = os.listdir(curProfilesPath)
            if len(profileChildren) > 0:
                return curProfilesPath + "/"
    raise Exception("Could not find Firefox profile path")
    
    
# def findLatestFileInDir(folder):
    # files = glob.glob(folder + "*") # * means all if need specific format then *.csv
    # latestFile = max(files, key=os.path.getctime)
    # return str(latestFile)


def removeExtraBitsTitle(title):
    # Remove special characters that mess with Windows's filesystem
    result = title.translate(str.maketrans("", "", '?<>|\"*:\\/'))

    # Remove YouTube's notification marker e.g. (35) plus a space, and other YouTube mp3 scraping artifacts
    regexes = ['\([0-9]*\)', 'y2mate\.is\s-\s', '\s-\sYouTube', '-.*-128k-\d*']
    for rgx_match in regexes:
        result = re.sub(rgx_match, '', result)

    return result.strip()


def traverseBookmarks(item):
    return traverseBookmarksHelper([], item)


def traverseBookmarksHelper(result, item):
    if not item: return
    if "children" in item:
        for i in range(len(item["children"])):
            traverseBookmarksHelper(result, item["children"][i])
    elif "uri" in item:
        uri = item["uri"]
        title = item["title"]

        title = removeExtraBitsTitle(title)

        print(title.encode("utf-8"), flush=True)

        time = item["dateAdded"]
        if "youtube.com/watch?v=" in uri:
            ytBookmark = dict()
            ytBookmark["uri"] = uri
            ytBookmark["title"] = title
            ytBookmark["time"] = time
            result.append(ytBookmark)
    return result


def reporthook(count, block_size, total_size):
    global start_time
    if count == 0:
        start_time = time.time()
        return
    duration = time.time() - start_time
    progress_size = int(count * block_size)
    speed = int(progress_size / (1024 * duration))
    percent = int(count * block_size * 100 / total_size)
    sys.stdout.write("\r...%d%%, %d MB, %d KB/s, %d seconds passed" %
                    (percent, progress_size / (1024 * 1024), speed, duration))
    sys.stdout.flush()
        

def downloadMusicOrUseCache(url, title):
    if "&" in url:
        url = url.split("&")[0]
    print(("Attempting to get title: " + title).encode("utf-8"), flush=True)
    print(url, flush=True)
    try:
        outputPath = "./output/" + title + ".mp3"
        existingFile = Path(outputPath)
        existingIgnoredFile = Path("./ignore/" + title + ".mp3")
        if not existingFile.is_file() and not existingIgnoredFile.is_file():
            ytAudioData = os.popen(ytExe + " -N 8 -x --get-url \"" + url + "\" --get-duration --downloader=aria2c --downloader-args \"aria2c:--continue --min-split-size=1M --max-connection-per-server=16 --max-concurrent-downloads=16 --split=16\"").readlines()
            ytAudioUrl = ytAudioData[0]

            #Do not download files that are obviously way too long or short
            ytDurationString = ytAudioData[1]
            tokens = ytDurationString.split(":")
            minutes = int(tokens[0])

            if minutes >= 1 and minutes < 8 and len(tokens) == 2: #"2 hours 9 minutes 20 seconds => [2,9,20]"
                print("Downloading song title: ", flush=True)
                print(str(title).encode("utf-8"), flush=True)
                print("", flush=True)
                # urllib.request.urlretrieve(ytAudioUrl, outputPath, reporthook)
                r = requests.get(ytAudioUrl)
                r.raise_for_status()
                with open(outputPath, 'wb') as f:
                    f.write(r.content)
                print("\n", flush=True)
                return True
            else:
                print("Audio length too long or too short", flush=True)
        else:
            print("Found file in cache", flush=True)
    except Exception as e:
        print("The download code error: " + str(e), flush=True)
        return "Error during download"
    print("Skipping: ", flush=True)
    print(str(title).encode("utf-8"), flush=True)
    print("", flush=True)
    return False


def downloadMusic(url, title):
    actuallyDownloadedFile = downloadMusicOrUseCache(url, title)
    if actuallyDownloadedFile is False:
        try:
            with open('./ignore/' + title + '.mp3', 'w') as fp:
                pass
        except:
            pass
    return actuallyDownloadedFile


def removeDupesAndSanitize(folderName):
    seenNames = set()
    for file in os.listdir(folderName):
        if ".mp3" in file:
            sanitizedName = removeExtraBitsTitle(file)
            if sanitizedName in seenNames:
                # print("Removed: " + folderName + file)
                # print("because of: " + sanitizedName)
                # print("-----")
                os.remove(folderName + file)
            else:
                seenNames.add(sanitizedName)
                if not Path(folderName + sanitizedName).exists():
                    os.rename(folderName + file, folderName + sanitizedName)


def main():
    createFolderIfNonexistent("./output/")
    createFolderIfNonexistent("./ignore/")

    downloaded = 0

    removeDupesAndSanitize("./output/")

    # Create a SQL connection to our SQLite database
    con = sqlite3.connect(findFirefoxPath() + "places.sqlite")
    cur = con.cursor()
    print("Executing sqlite query...")
    for row in cur.execute("SELECT * FROM moz_bookmarks;"):
        #print(str(row).encode("utf-8"), flush=True)
        
        if row[2] is not None:
            con2 = sqlite3.connect(findFirefoxPath() + "places.sqlite")
            cur2 = con2.cursor()
            for place in cur2.execute("SELECT * FROM moz_places WHERE id=" + str(row[2]) + ";"):
                #print(place, flush=True)
                if "youtube.com/watch?v=" in place[1]:
                    #print(str(place[1]) + "; " + str(place[2]), flush=True)
                    actuallyDownloadedFile = downloadMusic(place[1], removeExtraBitsTitle(place[2]))
                    if actuallyDownloadedFile:
                        downloaded = downloaded + 1
                        print(str(downloaded) + " YouTube urls found", flush=True)
        
    print("Downloads complete", flush=True)
