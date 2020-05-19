# emojibot2
A bot for inserting relevant emoji into copypasta or other text

# Getting started

Dependencies: `praw`, `requests`

Skip to step 3 if you want to use the prebuilt emoji database (`edb.prebuilt.json`)

1. Download all* the posts off r/emojipasta by running `reddit_dl.py`
2. Process them into an Emoji Database (EDB) by running `emojifier.py` (by itself not as a module) *
3. Modify `bot.template.py` to include your API key and run


*the algorithm I wrote for this is very unoptimized, it took around 20 minutes to process all 3000+ posts from r/emojipasta

** i used the pushshift api for this it might not be *every single post* but yknow