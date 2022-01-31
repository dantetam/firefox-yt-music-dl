Firefox Favorites JSON Music Downloader
============
This is a code doodle that automatically downloads music from YouTube links in my Firefox bookmarks. I have a habit of putting songs I like into the toolbar and forgetting about them. This also downloads music from history files, from YT links that have been visited at least five times.

Put your Firefox bookmarks .json file path into the variable `chosenBookmarkFileName`. Run the program. The program will never download files that are already present in the folders `output` and `ignore`.

Run history downloads:
```
python -c "import history; print(history.main())"
```

Run bookmark downloads:
```
python -u base.py
```

Tech Details
-----------------
Bookmark data is represented in a nested JSON format with an arbitrary number of nested folders containing bookmarks and folders. Bookmarks contain the title of the website, the URL, and the time of their creation. The [YouTube DL library](https://github.com/ytdl-org/youtube-dl) and [its more convenient fork](https://github.com/yt-dlp/yt-dlp/) are APIs used to generate downloadable media links which this program uses to download music, and also provide data about the YouTube video such as its duration. This program specifically downloads audio only.

History files are

Quandaries
-----------------
Google has grown to be one of the most profitable companies in history by scraping the web and loading other people's servers without permission and any promise of a royalty beyond exposure. If anything, this saves them bandwidth, especially if I turned on my ad blocker.
