import argparse
import logging

import lib.get_titles_list
import lib.collect_wikis


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Wiki Editors Collector")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--force_start", "-f", type=int, default=2,
                        help="Level from where you want to force deletion, deault : not forced")
    parser.add_argument("--workers", "-w", type=int, default=1,
                        help="Number of worker processes for crawling data, default : single process")
    parser.add_argument("--log_file", "-lf", default=None, help="Set path to save log output")

    args = parser.parse_args()

    log_file_handler = None
    if args.log_file:
        log_file_handler = logging.FileHandler(args.log_file)
        formatter = logging.Formatter('[%(asctime)s] [%(processName)s/%(levelname)s] %(message)s')
        log_file_handler.setFormatter(formatter)

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # Start anew by fetching wikipedia titles, level 0
    lib.get_titles_list.save_titles_to_collect(log_handler=log_file_handler,
                            force_start=True if args.force_start == 0 else False)

    # Start anew by creating database of title pages and users database, level 1
    lib.collect_wikis.start_collect(log_handler=log_file_handler, pool_size=args.workers,
                            force_start=True if args.force_start <= 1 else False)
