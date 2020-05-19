from db import Database
import emoji
import json
import time
import random

db = Database("emojipasta")

def is_emoji(char):
    return char in emoji.UNICODE_EMOJI

def handle_dual_emojis(string):
    i = 0
    chars = []
    while i < len(string):
        c = string[i]
        for e in emoji.UNICODE_EMOJI:
            #print((e,len(e)))
            if string[i:i + len(e)] == e:
                c = e

        chars.append(c)
        i+=len(c)
    return chars

def extract_last_word(string, from_index):
    i = from_index-1
    word = ""
    while i >= 0:
        #print((i, word, remove_emoji(word), is_blank_string(remove_emoji(word))))
        if string[i] == " " and not is_blank_string(remove_emoji(word)):
            return word.strip()
        word=string[i]+word
        i-=1
    return word.strip()

def is_blank_string(s):
    return s.strip() == ""

def remove_emoji(s):
    return "".join(filter(lambda c: not is_emoji(c), s))

def emoji_ratio(s):
    if len(s) == 0:
        return 0
    return 1 - (len(remove_emoji(s)) / len(s))

def num_emoji(s):
    return len(s) - len(remove_emoji(s))

def only_alphanumerics(s):
    chars = "abcdefghijklmnopqrstuvwxyz1234567890_-ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    s = "".join(filter(lambda c: c in chars, s))
    return s

class EmojiDB:
    def __init__(self):
        self.data = {}
    
    def load_from_file(self, path):
        with open(path) as fl:
            self.data = json.load(fl)
    
    def write_entry(self, word, emoji):
        word = only_alphanumerics(word.lower())

        if is_blank_string(word):
            return
        
        if not word in self.data:
            self.data[word] = []
        
        self.data[word].append(emoji)
    
    def read_entry(self, word):
        word = only_alphanumerics(word.lower())

        return self.data.get(word, None)
    
    def has_entry(self, word):
        return self.read_entry(word) != None
        
    def emojify(self, text, len_probabilities=[1, 1, 1, 1, 2, 2, 3]):
        emojified = ""
        for word in text.split(" "):
            if self.has_entry(word):
                emoji_string = ""
                for i in range(random.choice(len_probabilities)):
                    emoji_string+=random.choice(self.read_entry(word))
                
                emojified+=word+emoji_string+" "
            else:
                emojified+=word+" "
        return emojified
            
    
    def digest(self, text):
        text = handle_dual_emojis(text)
        for index, char in enumerate(text):
            if is_emoji(char):
                word = extract_last_word(text, index).lower()
                
                self.write_entry(remove_emoji(word), char)
    
    def build_from_reddit_db(self, db):
        data = db.aggregate_data()
        i = 1
        st = time.time()
        for post in data:
            dt = time.time()-st
            time_per_post = dt / i
            remaining_time = time_per_post * (len(data)-i)
            print("Processing post {}/{} ({}%) [remaining time: {}] [edb size: {}] [post text size: {}]".format(
                i,
                len(data),
                int(i/len(data)*100),
                time.strftime('%H:%M:%S', time.gmtime(remaining_time)),
                len(self.data),
                len(post["selftext"]+post["title"])
            ))

            # don't bother with posts that are over 50% emoji
            if emoji_ratio(post["selftext"]) > 0.5:
                print("skipping")
                i+=1
                continue

            self.digest(post["selftext"])
            self.digest(post["title"])
            i+=1
            self.save()
    
    def save(self, to="edb.json"):
        with open(to, "w") as fl:
            json.dump(self.data, fl, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    edb = EmojiDB()
    edb.load_from_file("edb.json")
    edb.build_from_reddit_db(db)
    edb.save()
# edb.load_from_file("edb.json")
# with open("in.txt") as fl:
#     test = fl.read()

# with open("out.txt", "w") as fl:
#     fl.write(edb.emojify(test))