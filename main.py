import argparse
import logging
import logging.config

from loadcfg import CFG

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
    cfg_parser.load()
    logger.info(cfg_parser.tokens)
    # for token in cfg_parser.tokens:
    #     logger.info(token)
    # for keyword in cfg_parser.keywords:
    #     logger.info(keyword)
    # for directive in cfg_parser.directives:
    #     logger.info(directive)
    for name, rule in cfg_parser.name_to_rule.items():
        logger.info("%s: %s" % (name, rule))
    for name, rule in cfg_parser.directives.items():
        logger.info("%s: %s" % (name, rule))






if __name__ == "__main__":
    main()

