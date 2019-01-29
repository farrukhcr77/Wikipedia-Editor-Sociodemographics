import logging
import multiprocessing

import utils.db_interface
from lib.globalvs import (LIMIT_WORKFORCE, QUEUE_MAX_SIZE, DB_NAME, EDITORS_TABLE)

logger = multiprocessing.log_to_stderr()


def queue_feeder(q, log_fh=None, force_refresh=False):
    db_api = utils.db_interface.DBHandler(db_name=DB_NAME, log_handler=log_fh)
    if force_refresh:
        db_api.update(table_name=EDITORS_TABLE, find_q={}, update_q={"info" : {}})
        time.sleep(2)
    while True:
        if q.empty():
            all_entries = db_api.find(table_name=EDITORS_TABLE, limit_n=QUEUE_MAX_SIZE,
                                      query={"info" : {"$eq" : {}}},
                                      return_cols=["_id", "id", "raw_content"])
            for entry in all_entries:
                q.put(entry)
        else:
            # Keep checking every 2 seconds
            time.sleep(2)


def queue_consumer(q, id, log_fh=None):
    db_api = utils.db_interface.DBHandler(db_name=DB_NAME, log_handler=log_fh)
    time.sleep(2)
    while True:
        if not q.empty():
            find_id, editor_id, raw_content = q.get()
            
        else:
            time.sleep(2)


def start_analysis(force=False, pool_size=1, log_handler=None):
    if log_handler:
        logger.addHandler(log_handler)
    if pool_size > LIMIT_WORKFORCE:
        logger.error("Number of workers cannot be more than {}".format(LIMIT_WORKFORCE))
        return
    logger.info("Number of processes crawling data : {}".format(pool_size))
    editors_queue = multiprocessing.Queue(QUEUE_MAX_SIZE)
    feeder = multiprocessing.Process(target=queue_feeder,
                         kwargs=dict(q=editors_queue, log_fh=log_handler,
                                     force_refresh=force))
    feeder.start()
    workers = []
    for i in range(pool_size):
        worker_process = multiprocessing.Process(target=queue_consumer, name="Worker-{}".format(i),
                                kwargs=dict(q=editors_queue, log_fh=log_handler, id=i))
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
