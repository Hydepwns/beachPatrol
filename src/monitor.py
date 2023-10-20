from celery import shared_task
from twitter import get_twitter_space_if_live
import redis
from celery_config import app as celery_app
import time

r = redis.Redis(host='localhost', port=6380)


@shared_task
def check_if_live():
    print("Checking if live...")
    urls_to_check = r.lrange('watchlist', 0, -1)
    for url in urls_to_check:
        url_str = url.decode('utf-8')
        tw_space = get_twitter_space_if_live(url_str, "../cookies.txt")
        if (tw_space is not None):
            print(f"Space {url_str} is live!")
            print(tw_space["url"])
            if (r.get(f"scraping:{url_str}") == "True"):
                print(f"Already scraping {url_str}, skipping...")
                continue
            r.set(f"scraping:{url_str}", "True")
            celery_app.send_task('worker.scrape_space', args=[
                                 tw_space["url"], True])
