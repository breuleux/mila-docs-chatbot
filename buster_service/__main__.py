import argparse
import importlib
import sys
from pathlib import Path

import yaml
from grizzlaxy import grizzlaxy

from .app import cfg, chat


def _config(options):
    cfg_file = Path(options.config)
    with open(cfg_file) as f:
        config = yaml.safe_load(f)
    return config, cfg_file.parent


def command_web(options):
    config, directory = _config(options)

    cfg.configure(config)

    grizzlaxy(
        module=chat,
        **config["grizzlaxy"],
        relative_to=directory,
    )


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

    for method in methods:
        module = importlib.import_module(f"buster_service.acquire.{method}")
        module.main(
            global_config=config,
            config=aconfig[method],
            options=options,
        )


def main():
    parser = argparse.ArgumentParser(description="Start Buster server.")
    subparsers = parser.add_subparsers(required=True, dest="command")
    web = subparsers.add_parser("web")
    web.add_argument("--config", help="Configuration file.", required=True)

    acquire = subparsers.add_parser("acquire")
    acquire.add_argument("method", help="Acquisition method.")
    acquire.add_argument("--config", help="Configuration file.", required=True)
    acquire.add_argument("--anew", action="store_true", help="Start generation anew.")

    options = parser.parse_args()
    globals()[f"command_{options.command}"](options)


if __name__ == "__main__":
    main()
