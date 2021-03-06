import argparse
import logging
import logging.config

from loadcfg import CFG

logger = logging.getLogger(__name__)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs='?', type=str)
    parser.add_argument("--grammar", type=str, default="clive.grm")
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()

    log_level = logging.INFO
    if args.verbose:
        log_level = logging.DEBUG
        print("verbose logging enabled")

    logging.basicConfig(level=log_level,
                        format='%(asctime)s | %(name)s:%(lineno)s |%(levelname)-7s| %(message)s')

    logger.debug("opening file")
    cfg_parser = CFG(args.grammar)
    cfg_parser.load()
    logger.info(cfg_parser.tokens)
    for name, rule in cfg_parser.name_to_rule.items():
        logger.info("%s: %s" % (name, rule))
    for name, rule in cfg_parser.directives.items():
        logger.info("%s: %s" % (name, rule))

    tokens = cfg_parser.tokenize_file(args.file)
    for token in tokens:
        logger.info(token)

    matches = cfg_parser.matches(tokens)






if __name__ == "__main__":
    main()

