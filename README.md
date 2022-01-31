Firefox Favorites JSON Music Downloader
============
This is a code doodle that automatically downloads music from YouTube links in my Firefox bookmarks. I have a habit of putting songs I like into the toolbar and forgetting about them.

Put your Firefox bookmarks .json file path into the variable `chosenBookmarkFileName`. Run the program. The program will never download files that are already present in the folders `output` and `ignore`.

TODO: Download music from history (.sqlite) files, architect this project better for that (and maybe other browsers). Use sites that meet the music criteria that have been visited at least five times.


Tech Details
-----------------
Bookmark data is represented in a nested JSON format with an arbitrary number of nested folders containing bookmarks and folders. Bookmarks contain the title of the website, the URL, and the time of their creation. The [YouTube DL library](https://github.com/ytdl-org/youtube-dl) and [its more convenient fork](https://github.com/yt-dlp/yt-dlp/) are APIs used to generate downloadable media links which this program uses to download music, and also provide data about the YouTube video such as its duration. This program specifically downloads audio only.


Quandaries
-----------------
Google has grown to be one of the most profitable companies in history by scraping the web and loading other people's servers without permission and any promise of a royalty beyond exposure. If anything, this saves them bandwidth, especially if I turned on my ad blocker.
