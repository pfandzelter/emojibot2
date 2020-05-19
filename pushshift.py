import requests
import time

class RateLimiter:
    def __init__(self, rate): # rate is requests / min
        self.rate = rate
        self.last_request_ts = 0
    
    def limit(self):
        min_delay_sec = 60/self.rate

        while time.time() - self.last_request_ts < min_delay_sec:
            pass
        
        self.last_request_ts = time.time()
        
def check_rate_limit():
    return requests.get("https://api.pushshift.io/meta").json()["server_ratelimit_per_minute"]

rate_limiter = RateLimiter(check_rate_limit() - 20)

def submissions(subreddit, start_ts, end_ts):
    rate_limiter.limit()

    resp = requests.get("https://api.pushshift.io/reddit/submission/search", params={
        "after": int(start_ts),
        "before": int(end_ts),
        "sort": "desc",
        "subreddit": subreddit
    })

    if resp.status_code == 429: # rate limited
        print("warning: ratelimited")
        time.sleep(5)
        return submissions(subreddit, start_ts, end_ts)

    return resp.json()

def get_block(subreddit, now, block=0, blocksize=1209600):
    """ return submissions in a "block" (i.e. fixed-size time units of submissions) ascending back in time """

    # default blocksize = 2 weeks

    start_ts = now-(block+1)*blocksize
    end_ts = start_ts+blocksize

    return submissions(subreddit, start_ts, end_ts)

def less_data(data):
    for i in range(len(data)):
        submission = data[i]
        data[i] = {
            "selftext": submission.get("selftext", ""),
            "title": submission["title"],
            "permalink": submission["permalink"]
        }

    return data