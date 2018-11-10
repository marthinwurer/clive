import argparse
import logging
import logging.config

from tokenizer import FileTokenizer

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s | %(name)s:%(lineno)s |%(levelname)-7s| %(message)s')

    logger.debug("Parsing Args")
    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs='?', type=str)

    args = parser.parse_args()

    with open(args.file) as file:
        tokens = FileTokenizer(file).tokenize_file()
    for tok in tokens:
        logger.info(tok)






if __name__ == "__main__":
    main()

