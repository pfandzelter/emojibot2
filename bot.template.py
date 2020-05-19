"""

This file is a copy of the actual bot code minus my API key for obvious reasons. It won't run as is

"""

import emojifier
import praw

reddit = praw.Reddit()

edb = emojifier.EmojiDB()
edb.load_from_file("edb.json")

subreddit = reddit.subreddit("copypasta")

for post in subreddit.stream.submissions(skip_existing=True):
    text = post.title
    if post.selftext:
        text = post.selftext

    try:
        if emojifier.emoji_ratio(text) < 0.05:
            comm = post.reply(edb.emojify(text))

            print("https://reddit.com"+comm.permalink)
    except Exception as e:
        print(e)