import json
import pushshift
import time
import os
import glob


class DBException(Exception):
    pass


class Database:
    def __init__(self, subreddit):
        self.subreddit = subreddit

    def init_header(self):
        with open("header.json", "w") as fl:
            json.dump({
                "now": int(time.time()),
                "current_block": 0, # the next block
                "blocksize": 1209600,
                "subreddit": self.subreddit
            }, fl)
    
    def update_header(self, current_block):
        header = self.load_header()
        with open("header.json", "w") as fl:
            header["current_block"] = current_block
            json.dump(header, fl)

    def load_header(self):
        with open("header.json") as fl:
            return json.load(fl)

    def validate_block_meta(self, meta):
        header = self.load_header()

        if meta["now"] == header["now"] and meta["blocksize"] == header["blocksize"] and meta["subreddit"] == header["subreddit"]:
            return True

    def load_block_data(self, block):
        if not os.path.exists("header.json"):
            raise DBException("Search header not present. Data is invalid")

        with open(f"blocks/block{block}.json") as fl:
            data = json.load(fl)

            if not self.validate_block_meta(data["meta"]):
                raise DBException("Block metadata does not match search header")
                
        return data["data"]

    def resume_search(self):
        if not os.path.exists("blocks"):
            os.mkdir("blocks")
            
        if not os.path.exists("header.json"):
            raise DBException("Search header not present. Try calling .init_header()")

        header = self.load_header()

        block = header["current_block"]
        while 1:
            data = pushshift.get_block(self.subreddit, header["now"], block=block, blocksize=header["blocksize"])["data"]
            data = pushshift.less_data(data)
            if not data:
                return

            with open(f"blocks/block{block}.json", "w") as fl:
                json.dump({
                    "data": data,
                    "meta": {
                        "now": header["now"],
                        "blocksize": header["blocksize"],
                        "subreddit": self.subreddit
                    }
                }, fl)
            
            block+=1
            self.update_header(block)
    
    def num_db_blocks(self):
        if not os.path.exists("header.json"):
            raise DBException("Search header not present")

        return self.load_header()["current_block"]-1
    
    def aggregate_data(self):
        if not os.path.exists("header.json"):
            raise DBException("Cannot aggregate data: search header not present")
        data = []
        header = self.load_header()
        for block in range(header["current_block"]):
            data+=self.load_block_data(block)
        
        return data

    def clear_database(self):
        for fl in glob.glob("blocks/*.json"):
            os.remove(fl)