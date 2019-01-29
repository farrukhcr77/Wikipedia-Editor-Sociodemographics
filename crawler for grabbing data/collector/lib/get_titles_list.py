import click
import gzip
import logging
import os
import urllib.request

from lib.globalvs import ALL_TITLES, TITLES_DUMP, DUMP_PATH


def save_titles_to_collect(force_start=False, log_handler=None):
    logger = logging.getLogger(__name__)
    if log_handler:
        logger.addHandler(log_handler)
    if not os.path.exists(DUMP_PATH):
        os.mkdir(DUMP_PATH)
    else:
        if force_start:
            if os.path.exists(ALL_TITLES):
                os.rename(ALL_TITLES, "{}_BACKUP".format(ALL_TITLES))
                logger.debug("Kept a backup copy of titles already found as _BACKUP")
        if os.path.exists(ALL_TITLES):
            logger.debug("Titles are already present, nothing to do here ...")
            return

    with urllib.request.urlopen(TITLES_DUMP) as response, open(ALL_TITLES, "wb") as f:
        length_of_data = int(response.getheader("content-length"))
        with click.progressbar(length=length_of_data,
                    label="Downloading Wikipedia Titles List ... ") as progress:
            chunk_size = 2497 * 1024
            while True:
                buffer = response.read(chunk_size)
                if not buffer:
                    break
                f.write(buffer)
                progress.update(chunk_size)

    with open(ALL_TITLES, "rb") as f, open("{}_W".format(ALL_TITLES), "wb") as fw:
        fw.write(gzip.decompress(f.read()))
    os.remove(ALL_TITLES)
    os.rename("{}_W".format(ALL_TITLES), ALL_TITLES)
    if os.path.exists("{}_BACKUP".format(ALL_TITLES)):
        os.remove("{}_BACKUP".format(ALL_TITLES))
    logger.debug("All Wikipedia Titles saved in path - {}".format(ALL_TITLES))
