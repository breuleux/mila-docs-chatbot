import os
import shutil
import subprocess
from argparse import ArgumentParser
from pathlib import Path

import pandas as pd
import yaml
from buster.docparser import generate_embeddings, get_all_documents
from buster.documents.sqlite.documents import DocumentsDB
from buster.parser import SphinxParser

here = Path(__file__).parent


def process_docs(name, config, options):
    base = Path(options.base)
    if not base.is_absolute():
        base = Path.cwd() / base

    repo_path = base / config["repo"]

    if options.anew:
        shutil.rmtree(repo_path)

    results = subprocess.run(
        here / "refresh-repo.sh",
        env={
            "BASE": base,
            "REPO": config["repo"],
            "BRANCH": config["branch"],
            "REQFILE": config["requirements"],
            **os.environ,
        },
    )

    if results.returncode == 0:
        print("Chunking the documents...")

        # Docs in HTML format
        outdir = repo_path / config["output"]

        # URL that will be prefixed to all chunk links
        base_url = config["base_url"]

        # Parser to use, you can create one by inheriting from buster.parser.Parser
        parser = SphinxParser

        # Path to output CSV file
        output_csv = base / f"{name}.csv"

        # Create the chunks, returns a DataFrame
        documents_df = get_all_documents(outdir, base_url, parser)

        # The source column is used to easily filter/update the documents. We could have mila-docs, slack-threads, office-hours, ...
        documents_df["source"] = name

        # Save the chunks
        documents_df.to_csv(output_csv, index=False)

        print("Generating the embeddings...")

        # Generate the embeddings
        documents_manager = DocumentsDB(options.db)

        documents = pd.read_csv(output_csv)
        documents = generate_embeddings(documents, documents_manager, 500, "text-embedding-ada-002")


def main():
    parser = ArgumentParser(description="Acquire Sphinx docs.")

    parser.add_argument("config", help="Configuration file.")
    parser.add_argument("--anew", action="store_true", help="Start generation anew.")
    parser.add_argument("--base", required=True, help="Base directory for the docs.")
    parser.add_argument("--db", required=True, help="Path to the database.")

    options = parser.parse_args()

    config = yaml.safe_load(open(options.config, "r"))
    for key, settings in config.items():
        process_docs(key, settings, options)


if __name__ == "__main__":
    main()
