import os
import praw
import schedule
import random
import time
import configparser
import threading

try:
    import queue
except ImportError:
    import Queue as queue


config = configparser.ConfigParser()
config.read('conf.ini')
reddit_user = config['REDDIT']['reddit_user']
reddit_pass = config['REDDIT']['reddit_pass']
reddit_client_id = config['REDDIT']['reddit_client_id']
reddit_client_secret = config['REDDIT']['reddit_client_secret']
reddit_target_subreddit = config['REDDIT']['reddit_target_subreddit']
post_time = config['SETTINGS']['post_time']

video_in_dir = 'videos/'
stopper = 0


reddit = praw.Reddit(
    username=reddit_user,
    password=reddit_pass,
    client_id=reddit_client_id,
    client_secret=reddit_client_secret,
    user_agent='Reddit Daily video (by u/impshum)'
)

reddit.validate_on_submit = True


def set_stopper():
    global stopper
    stopper = 1


def get_random_video(dir):
    videos = [x for x in os.listdir(dir) if x.endswith(
        ('jpg', 'jpeg', 'png', 'gif', 'mp4', 'mkv'))]

    if not videos:
        set_stopper()
        print('No videos')
        return

    video = random.choice(videos)
    title = os.path.splitext(video)[0].replace('_', ' ')
    return {'video': video, 'title': title}


def runner():
    while 1:
        job_func = jobqueue.get()
        job_func()
        jobqueue.task_done()
        if stopper:
            break


def main():
    random_video = get_random_video(video_in_dir)
    if random_video:
        title = random_video['title']
        video = os.path.abspath(video_in_dir + random_video['video'])
        reddit.subreddit(reddit_target_subreddit).submit_video(title, video)
        os.remove(video)
        print(title)

jobqueue = queue.Queue()

# schedule options
schedule.every(10).seconds.do(jobqueue.put, main)
# schedule.every(3).minutes.do(jobqueue.put, main)
# schedule.every().hour.do(jobqueue.put, main)
# schedule.every().monday.do(jobqueue.put, main)

#schedule.every().day.at(post_time).do(jobqueue.put, main)

worker_thread = threading.Thread(target=runner)
worker_thread.start()

while True:
    schedule.run_pending()
    time.sleep(1)
    if stopper:
        worker_thread.join()
        break
