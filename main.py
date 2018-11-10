import argparse
import logging
import logging.config
import sys

from loadcfg import CFG
from tokenizer import FileTokenizer

logger = logging.getLogger(__name__)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs='?', type=str)
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()

    log_level = logging.INFO
    if args.verbose:
        log_level = logging.DEBUG
        print("verbose logging enabled")

    logging.basicConfig(level=log_level,
                        format='%(asctime)s | %(name)s:%(lineno)s |%(levelname)-7s| %(message)s')

    logger.debug("opening file")
    cfg_parser = CFG(args.file)
    cfg_parser.parse_file()






if __name__ == "__main__":
    main()

