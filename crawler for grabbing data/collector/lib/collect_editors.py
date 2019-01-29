import datetime
import logging
import multiprocessing
import os
import time
from urllib.error import URLError
from urllib.request import urlopen

import lib.content_cleaner
import utils.db_interface
from lib.content_parsers import EditorInfoParser
from lib.globalvs import (LIMIT_WORKFORCE, DB_NAME, EDITORS_TABLE, EXPIRE_AFTER,
                          QUEUE_MAX_SIZE, FAILED_CRAWLING_EDITORS)

logger = multiprocessing.log_to_stderr()


def queue_feeder(q, log_fh=None, force_refresh=False):
    db_api = utils.db_interface.DBHandler(db_name=DB_NAME, log_handler=log_fh)
    if force_refresh:
        db_api.update(table_name=EDITORS_TABLE, find_q={},
                      update_q={"last_updated" : datetime.datetime.fromtimestamp(0)})
        time.sleep(2)
    while True:
        if q.empty():
            expired_if_before = datetime.datetime.now() - datetime.timedelta(days=EXPIRE_AFTER)
            get_entries_before = {"last_updated" : {"$lt" : expired_if_before}}
            all_entries = db_api.find(table_name=EDITORS_TABLE, query=get_entries_before,
                                 return_cols=["_id", "id", "link"], limit_n=QUEUE_MAX_SIZE)
            for entry in all_entries:
                q.put(entry)
        else:
            # Keep checking every 2 seconds
            time.sleep(2)


def queue_consumer(q, id, file_write_lock, log_fh=None):
    db_api = utils.db_interface.DBHandler(db_name=DB_NAME, log_handler=log_fh)
    parser = EditorInfoParser(log_handler=log_fh)
    time.sleep(2)
    while True:
        if not q.empty():
            raw_content = ""
            editor_info = q.get()
            parse_links = [editor_info["link"],]
            logger.info("Fetching info for Editor : {}".format(editor_info["id"]))
            while parse_links:
                get_link = parse_links.pop()
                parser.reset()
                try:
                    with urlopen(get_link) as ufo:
                        parser.feed(ufo.read().decode("utf-8"))
                    if parser.has_userbox_page:
                        parse_links.append("{}/Userboxes".format(get_link))
                    raw_content += parser.get_data()
                except URLError as e:
                    # It's possible that the internet connection is kaputt, check by pinging Wikipedia
                    try:
                        cf = urlopen("https://en.wikipedia.org")
                    except URLError:
                        parse_links.append(get_link)
                        # internet is indeed Kaputt, sleep and try after 5 mins
                        time.sleep(300)
                        continue
                except Exception as e:
                    # No responsibility for any other errors
                    logger.error("Failed while collecting for editor - {}, {} : {}".
                            format(editor_info["id"], type(e).__name__, str(e)))
                    file_write_lock.acquire()
                    with open(FAILED_CRAWLING_EDITORS, "a") as ffw:
                        error_temp = "----------\n{editor}\n{name} : {body}\n------------"
                        ffw.write(error_temp.format(editor=editor_info["link"],
                                                    name=type(e).__name__, body=str(e)))
                    file_write_lock.release()
            raw_content = lib.content_cleaner.clean_editor_content(data=raw_content)
            db_api.update(table_name=EDITORS_TABLE, find_q={"_id" : editor_info["_id"]},
                                            update_q={"raw_content" : raw_content,
                                            "last_updated" : datetime.datetime.now()})
        else:
            # Just wait for something in Queue
            time.sleep(2)


def start_collect(force=False, pool_size=1, log_handler=None):
    if log_handler:
        logger.addHandler(log_handler)
    if pool_size > LIMIT_WORKFORCE:
        logger.error("Number of workers cannot be more than {}".format(LIMIT_WORKFORCE))
        return
    logger.info("Number of processes crawling data : {}".format(pool_size))
    editors_queue = multiprocessing.Queue(QUEUE_MAX_SIZE)
    write_lock = multiprocessing.Lock()
    feeder = multiprocessing.Process(target=queue_feeder,
                         kwargs=dict(q=editors_queue, log_fh=log_handler,
                                     force_refresh=force))
    feeder.start()
    workers = []
    for i in range(pool_size):
        worker_process = multiprocessing.Process(target=queue_consumer, name="Worker-{}".format(i),
                                kwargs=dict(q=editors_queue, log_fh=log_handler, id=i,
                                            file_write_lock=write_lock))
        worker_process.start()
        workers.append(worker_process)
    try:
        feeder.join()
        for w in workers:
            w.join()
    except KeyboardInterrupt:
        feeder.terminate()
        for w in workers:
            w.terminate()
        logger.error("Flow interrupted by user.. Exiting all worker threads ... ")
