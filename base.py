import json
import subprocess
import os
import urllib.request
import re
from pathlib import Path


# chosenBookmarkFileName = "./bookmarks/bookmarks-2022-06-22.json"
chosenBookmarkFileName = "./bookmarks/bookmarks-2023-03-10.json"
userDrivePath = "C:/Users/Dante" #no slash at right end

def createFolderIfNonexistent(path):
    existingFile = Path(path)
    if not existingFile.is_dir():
        os.makedirs(path)

def findFirefoxPath():
    profilesPath = userDrivePath + "/AppData/Roaming/Mozilla/Firefox/Profiles/"
    profilesDir = os.path.abspath(profilesPath)
    profiles = os.listdir(profilesDir)
    if len(profiles) > 0:
        profilesPath = profilesPath + profiles[0]
        return profilesPath + "/"




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
        #Remove special characters that mess with Windows's filesystem
        title = title.translate(str.maketrans("", "", '?<>|\"*:\\/'))
        print(title.encode("utf-8"), flush=True)
        time = item["dateAdded"]
        if "youtube.com" in uri:
            ytBookmark = dict()
            ytBookmark["uri"] = uri
            ytBookmark["title"] = title
            ytBookmark["time"] = time
            result.append(ytBookmark)
    return result

def downloadMusicOrUseCache(url, title):
    print("Attempting to get " + title)
    try:
        outputPath = "./output/" + title + ".mp3"
        existingFile = Path(outputPath)
        existingIgnoredFile = Path("./ignore/" + title + ".mp3")
        if not existingFile.is_file() and not existingIgnoredFile.is_file():
            ytAudioData = os.popen("yt-dlp-nightly-3-10-2023.exe -x --get-url \"" + url + "\" --get-duration").readlines()
            ytAudioUrl = ytAudioData[0]

            #Do not download files that are obviously way too long or short
            ytDurationString = ytAudioData[1]
            tokens = ytDurationString.split(":")
            minutes = int(tokens[0])

            if minutes >= 1 and minutes < 8 and len(tokens) == 2: #"2 hours 9 minutes 20 seconds => [2,9,20]"
                print("Downloading song title: ", flush=True)
                print(str(title).encode("utf-8"), flush=True)
                print("", flush=True)
                urllib.request.urlretrieve(ytAudioUrl, outputPath)
                return True
            else:
                print("Audio length too long or too short", flush=True)
        else:
            print("Found file in cache", flush=True)
    except Exception as e:
        print("The download code errored: " + str(e).encode("utf-8"), flush=True)
        return "Errored during download"
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

def main():
    createFolderIfNonexistent("./output/")
    createFolderIfNonexistent("./ignore/")
    downloadLimit = 100

    data = {}
    with open(chosenBookmarkFileName, encoding="utf8") as bookmarkFile:
        data = json.load(bookmarkFile)
        #print(str(data).encode("utf-8"))
        ytBookmarks = traverseBookmarks(data)
        #print(str(ytBookmarks).encode("utf-8"))

        for ytBookmark in ytBookmarks:
            #print(str(ytBookmark).encode("utf-8"))
            actuallyDownloadedFile = downloadMusic(ytBookmark["uri"], ytBookmark["title"])
            if actuallyDownloadedFile:
                downloadLimit = downloadLimit - 1
                if downloadLimit <= 0:
                    break

    print("Downloads complete", flush=True)
