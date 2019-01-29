import atexit
import logging
import multiprocessing
import os
import time
from urllib.error import URLError
from urllib.parse import quote
from urllib.request import urlopen

import utils.db_interface
from lib.content_parsers import WikiRevisionHistoryParser
from lib.globalvs import (ALL_TITLES, LIMIT_WORKFORCE, TITLES_MARK, FAILED_TITLES,
            DB_NAME, URL_TEMPLATE, PAGES_EDITS_TABLE, QUEUE_MAX_SIZE, EDITORS_TABLE)

logger = multiprocessing.log_to_stderr()
q = multiprocessing.Queue(QUEUE_MAX_SIZE)
in_process = {}


def complete_jobs(num_w, log_fh):
    for (worker, title) in in_process.items():
        q.put(title)
    write_lock = multiprocessing.Lock()
    workers = []
    for i in range(num_w):
        worker_process = multiprocessing.Process(target=queue_consumer, name="Worker-{}".format(i),
                                kwargs=dict(log_fh=log_fh, file_write_lock=write_lock, id=i))
        worker_process.start()
        workers.append(worker_process)
    for w in workers:
        w.join()
    logger.info("Completed all Worker jobs ... Gracefully exiting ..!!")


def queue_feeder(start_from=0):
    line = None
    fr = open(ALL_TITLES, "r")
    if start_from == 0:
        # The first line of the file, doesn't contain a title.
        # Ignore it.
        fr.readline()
    else:
        fr.seek(start_from)
    try:
        while True:
            if not q.full():
                line = fr.readline()
                if not line:
                    logger.info("Queue_Feeder:Done crawling info from all titles in the list")
                    break
                else:
                    title_name = line.strip()
                    logger.debug("Put {} to Queue".format(title_name))
                    q.put(tuple([fr.tell(), title_name]))
    except KeyboardInterrupt:
        pass
    finally:
        fr.close()


def queue_consumer(id, file_write_lock, log_fh):
    db_api = utils.db_interface.DBHandler(db_name=DB_NAME, log_handler=log_fh)
    time.sleep(1)
    worker_id = "Worker-{}".format(id)
    parser = WikiRevisionHistoryParser(db_api=db_api, log_handler=log_fh)
    processed_fpos = 0
    while not q.empty():
        processed_fpos, title_name = q.get()
        in_process[worker_id] = title_name
        logger.info("Crawling next for Wikipedia article titled - {}".format(title_name))
        parser.reset()
        parser.set_title(title_name)
        title_url = URL_TEMPLATE.format(t=quote(title_name))
        while True:
            try:
                with urlopen(title_url) as uf:
                    parser.feed(uf.read().decode("utf-8"))
                parser.push_to_db()
            except URLError as e:
                # It's possible that the internet connection is kaputt, check by pinging Wikipedia
                try:
                    cf = urlopen("https://en.wikipedia.org")
                except URLError:
                    # internet is indeed Kaputt, sleep and try after 5 mins
                    time.sleep(300)
                    continue
            except Exception as e:
                logger.error("{}:Error occurred for the title - {} ...".format(worker_id, title_name))
                logger.info("Check {} for further information".format(FAILED_TITLES))
                file_write_lock.acquire()
                with open(FAILED_TITLES, "a") as ffw:
                    error_temp = "----------\n{title}\n{name} : {body}\n------------"
                    ffw.write(error_temp.format(title=title_name, name=type(e).__name__,
                                                body=str(e)))
                file_write_lock.release()
            break
        in_process.pop(worker_id)

    # Check and write the maximum position till which titles have been crawled
    max_fpos = 0
    file_write_lock.acquire()
    if os.path.exists(TITLES_MARK):
        with open(TITLES_MARK, "r") as fr:
            max_fpos = int(fr.read())
    if max_fpos < processed_fpos:
        with open(TITLES_MARK, "w") as fw:
            fw.write(str(processed_fpos))
    file_write_lock.release()


def start_collect(force_start=False, pool_size=1, log_handler=None):
    if log_handler:
        logger.addHandler(log_handler)
    if pool_size > LIMIT_WORKFORCE:
        logger.error("Number of workers cannot be more than {}".format(LIMIT_WORKFORCE))
        return
    logger.info("Number of processes crawling data : {}".format(pool_size))
    db_api = utils.db_interface.DBHandler(db_name=DB_NAME, log_handler=log_handler)
    if force_start:
        if os.path.exists(TITLES_MARK):
            os.remove(TITLES_MARK)
        if os.path.exists(FAILED_TITLES):
            os.remove(FAILED_TITLES)
        db_api.delete_table(table_name=PAGES_EDITS_TABLE)
    db_api.index(table_name=EDITORS_TABLE, index_items=[("id", "ASCENDING")])
    set_start_mark = 0
    if os.path.exists(TITLES_MARK):
        with open(TITLES_MARK, "r") as fr:
            try:
                set_start_mark = int(fr.read())
            except ValueError:
                # Possible when the file is empty, let start be 0
                # Delete previous Wiki pages table if built
                db_api.delete_table(table_name=PAGES_EDITS_TABLE)
                if os.path.exists(FAILED_TITLES):
                    os.remove(FAILED_TITLES)

    atexit.register(complete_jobs, num_w=pool_size, log_fh=log_handler)
    write_lock = multiprocessing.Lock()
    feeder = multiprocessing.Process(target=queue_feeder, name="Title Feeder",
                                     kwargs=dict(start_from=set_start_mark))
    feeder.start()
    workers = []
    for i in range(pool_size):
        worker_process = multiprocessing.Process(target=queue_consumer, name="Worker-{}".format(i),
                        kwargs=dict(log_fh=log_handler, file_write_lock=write_lock, id=i))
        worker_process.start()
        workers.append(worker_process)
    try:
        feeder.join()
        for w in workers:
            w.join()
    except KeyboardInterrupt:
        logger.error("Trying to shut down all operations ... Do not press any key ")
        for w in workers:
            w.terminate()
        feeder.terminate()
