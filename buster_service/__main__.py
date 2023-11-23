import argparse
from pathlib import Path

import yaml
from grizzlaxy import grizzlaxy

from .app import cfg, chat


def main():
    parser = argparse.ArgumentParser(description="Start Buster server.")
    subparsers = parser.add_subparsers(required=True)
    web = subparsers.add_parser("web")
    web.add_argument("--config", help="Configuration file.", required=True)

    options = parser.parse_args()
    cfg_file = Path(options.config)
    with open(cfg_file) as f:
        config = yaml.safe_load(f)

    cfg.configure(config, relative_to=cfg_file.parent)

    grizzlaxy(
        module=chat,
        **config["grizzlaxy"],
        relative_to=cfg_file.parent,
    )


if __name__ == "__main__":
    main()
