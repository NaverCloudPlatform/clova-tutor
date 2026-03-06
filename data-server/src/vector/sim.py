# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import argparse
import os
import subprocess
import sys

from omegaconf import OmegaConf

root_path = (
    subprocess.check_output(["git", "rev-parse", "--show-toplevel"])
    .strip()
    .decode("utf-8")
)
sys.path.insert(1, os.path.join(root_path, "src"))

from common.logging import set_logger
from vector.service import VectorDBManager


def initialize_logger_and_builder(config_name, log_level):
    log_level = log_level.upper()

    if config_name == "make_db":
        logger_message = "Start making vectorstores from documents ... "
    elif config_name == "delete_db":
        logger_message = "Start removing vectorstores from documents index ... "
    elif config_name == "add_db":
        logger_message = "Start adding vectorstores from documents ... "
    elif config_name == "get":
        logger_message = "Fetching documents from Weaviate ... "
    elif config_name == "search":
        logger_message = "Start search vectorstores from query ... "
    else:
        raise ValueError(f"Unknown config name: {config_name}")

    logger = set_logger(logger_message, log_level)
    builder = VectorDBManager(logger=logger)

    return builder


def main():
    parser = argparse.ArgumentParser(description="VectorDB configuration")
    parser.add_argument("--config", type=str, default="config")
    parser.add_argument(
        "--loglevel",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="DEBUG",
        help="Logging level (default: INFO)",
    )
    args, _ = parser.parse_known_args()
    cfg = OmegaConf.load(f"config/{args.config}.yaml")
    if hasattr(cfg, "filter_info"):
        cfg.filter_info = OmegaConf.to_container(cfg.filter_info, resolve=True)

    builder = initialize_logger_and_builder(args.config, args.loglevel)
    if args.config == "make_db":
        builder.run(cfg.index_name, cfg.data_paths)
    else:
        if args.config == "delete_db":
            # Load the FAISS database from the specified index path
            builder.remove(cfg.index_name, cfg.docstore_ids)
        elif args.config == "add_db":
            builder.add(cfg.index_name, cfg.new_data_paths)
        elif args.config == "get":
            builder.get(cfg.index_name, cfg.docstore_ids)
        elif args.config == "search":
            builder.search(cfg.index_name, cfg.retrieve_info)
        else:
            raise NotImplementedError(f"{args.config} is not implemented.")
    builder.close()


if __name__ == "__main__":
    main()
