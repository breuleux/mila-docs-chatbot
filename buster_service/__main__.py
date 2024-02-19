import argparse
import importlib
from pathlib import Path
import sys
from types import SimpleNamespace

import gifnoc
from grizzlaxy import grizzlaxy


def command_web(configuration, options):
    if not Path(configuration.chatbot.buster["retriever_cfg"]["path"]).exists():
        command_acquire(configuration, SimpleNamespace(method="all", anew=True))

    configuration.chatbot.buster_object  # There is a weird bug if we don't fetch this now
    grizzlaxy(configuration.grizzlaxy)


def command_acquire(configuration, options):
    valid_methods = ["sphinx"]
    if options.method == "all":
        methods = valid_methods
    elif options.method not in valid_methods:
        sys.exit(f"Invalid method: {options.method}")
    else:
        methods = [options.method]

    for method in methods:
        module = importlib.import_module(f"buster_service.acquire.{method}")
        module.main(
            global_config=configuration,
            config=configuration.chatbot.acquire[method],
            options=options,
        )


def main():
    parser = argparse.ArgumentParser(description="Start Buster server.")

    subparsers = parser.add_subparsers(required=True, dest="command")
    subparsers.add_parser("web")

    acquire = subparsers.add_parser("acquire")
    acquire.add_argument("method", help="Acquisition method.")
    acquire.add_argument("--anew", action="store_true", help="Start generation anew.")

    with gifnoc.gifnoc(
        envvar="BUSTER_CONFIG",
        argparser=parser,
        sources=[{"grizzlaxy": {"module": "buster_service.app.chat"}}],
    ) as (cfg, options):
        globals()[f"command_{options.command}"](cfg, options)


if __name__ == "__main__":
    main()
