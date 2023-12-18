import argparse
import importlib
import sys
from pathlib import Path

import openai
import yaml
from grizzlaxy import grizzlaxy
from omegaconf import OmegaConf

from .app import cfg, chat


def _config(options):
    configs = []
    for filename in options.config:
        cfg_file = Path(filename)
        with open(cfg_file) as f:
            config = yaml.safe_load(f)
        directory = cfg_file.parent
        configs.append(config)
    return OmegaConf.merge(*configs), directory


def command_web(options):
    config, directory = _config(options)

    cfg.configure(config)

    grizzlaxy(module=chat, **config["grizzlaxy"])


def command_acquire(options):
    valid_methods = ["sphinx"]
    if options.method == "all":
        methods = valid_methods
    elif options.method not in valid_methods:
        sys.exit(f"Invalid method: {options.method}")
    else:
        methods = [options.method]

    config, directory = _config(options)
    aconfig = config["acquire"]

    # set openAI creds
    openai.api_key = config["openai_api_key"]

    for method in methods:
        module = importlib.import_module(f"buster_service.acquire.{method}")
        module.main(
            global_config=config,
            config=aconfig[method],
            options=options,
        )


def main():
    parser = argparse.ArgumentParser(description="Start Buster server.")
    parser.add_argument("--config", action="append", help="Configuration file.", required=True)

    subparsers = parser.add_subparsers(required=True, dest="command")
    subparsers.add_parser("web")

    acquire = subparsers.add_parser("acquire")
    acquire.add_argument("method", help="Acquisition method.")
    acquire.add_argument("--anew", action="store_true", help="Start generation anew.")

    options = parser.parse_args()
    globals()[f"command_{options.command}"](options)


if __name__ == "__main__":
    main()
