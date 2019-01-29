import argparse
import logging

import lib.startup_analysis


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze Content to extract information")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--force", "-f", action="store_true", help="Force refresh analysis on Data")
    parser.add_argument("--workers", "-w", type=int, default=1,
                        help="Number of worker processes for analysis, default : single process")
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

    lib.startup_analysis.start_analysis(force=args.force, pool_size=args.workers,
                                        log_handler=log_file_handler)
