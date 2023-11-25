import os
import shutil
import subprocess
from pathlib import Path

import pandas as pd
from buster.docparser import generate_embeddings, get_all_documents
from buster.documents.sqlite.documents import DocumentsDB
from buster.parser import SphinxParser

here = Path(__file__).parent


def process_docs(name, config, global_config, options):
    base = Path(global_config["data_dir"]) / "sphinx"
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
        documents_manager = DocumentsDB(global_config["database_path"])

        documents = pd.read_csv(output_csv)
        documents = generate_embeddings(documents, documents_manager, 500, "text-embedding-ada-002")


def main(global_config, config, options):
    for key, settings in config.items():
        process_docs(key, settings, global_config, options)
