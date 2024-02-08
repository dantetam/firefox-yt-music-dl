import json
import subprocess
import os
import urllib.request
import re
from pathlib import Path
import sys
import codecs

# sys.stdout = codecs.getwriter("iso-8859-1")(sys.stdout, 'xmlcharrefreplace')


# chosenBookmarkFileName = "./bookmarks/bookmarks-2022-06-22.json"
chosenBookmarkFileName = "./bookmarks/bookmarks-2023-03-10.json"
userDrivePath = "C:/Users/dante" #no slash at right end
ytExe = "yt-dlp-12-30-2023.exe" #"yt-dlp.exe"


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
        if "youtube.com" in uri:
            ytBookmark = dict()
            ytBookmark["uri"] = uri
            ytBookmark["title"] = title
            ytBookmark["time"] = time
            result.append(ytBookmark)
    return result


def downloadMusicOrUseCache(url, title):
    print(("Attempting to get " + title).encode("utf-8"))
    try:
        outputPath = "./output/" + title + ".mp3"
        existingFile = Path(outputPath)
        existingIgnoredFile = Path("./ignore/" + title + ".mp3")
        if not existingFile.is_file() and not existingIgnoredFile.is_file():
            ytAudioData = os.popen(ytExe + " -N 8 -x --get-url \"" + url + "\" --get-duration").readlines()
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
    downloadLimit = 100

    removeDupesAndSanitize("./output/")

    data = {}
    with open(chosenBookmarkFileName, encoding="utf8") as bookmarkFile:
        data = json.load(bookmarkFile)
        #print(str(data).encode("utf-8"))
        ytBookmarks = traverseBookmarks(data)
        #print(str(ytBookmarks).encode("utf-8"))

        for ytBookmark in ytBookmarks:
            #print(str(ytBookmark).encode("utf-8"))
            actuallyDownloadedFile = downloadMusic(ytBookmark["uri"], removeExtraBitsTitle(ytBookmark["title"]))
            if actuallyDownloadedFile:
                downloadLimit = downloadLimit - 1
                if downloadLimit <= 0:
                    break

    print("Downloads complete", flush=True)
