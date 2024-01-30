import glob
import os
import shutil
import subprocess
from pathlib import Path
from typing import Type

import pandas as pd
from bs4 import BeautifulSoup
from buster.documents_manager import DeepLakeDocumentsManager
from buster.parsers.parser import Parser, SphinxParser
from tqdm import tqdm

here = Path(__file__).parent


def get_document(
    root_dir: str,
    file: str,
    base_url: str,
    parser_cls: Type[Parser],
    min_section_length: int = 100,
    max_section_length: int = 2000,
) -> pd.DataFrame:
    """Extract all sections from one file.

    Sections are broken into subsections if they are longer than `max_section_length`.
    Sections correspond to `section` HTML tags that have a headerlink attached.
    """
    filepath = os.path.join(root_dir, file)
    with open(filepath, "r") as f:
        source = f.read()

    soup = BeautifulSoup(source, "html.parser")
    parser = parser_cls(soup, base_url, root_dir, filepath, min_section_length, max_section_length)

    sections = []
    urls = []
    names = []
    for section in parser.parse():
        sections.append(section.text)
        urls.append(section.url)
        names.append(section.name)

    documents_df = pd.DataFrame.from_dict({"title": names, "url": urls, "content": sections})

    return documents_df


def get_all_documents(
    root_dir: str,
    base_url: str,
    parser_cls: Type[Parser],
    min_section_length: int = 100,
    max_section_length: int = 2000,
) -> pd.DataFrame:
    """Parse all HTML files in `root_dir`, and extract all sections.

    Sections are broken into subsections if they are longer than `max_section_length`.
    Sections correspond to `section` HTML tags that have a headerlink attached.
    """
    files = glob.glob("**/*.html", root_dir=root_dir, recursive=True)

    dfs = []
    for file in tqdm(files):
        try:
            df = get_document(root_dir, file, base_url, parser_cls, min_section_length, max_section_length)
            dfs.append(df)
        except Exception as e:
            print(f"Skipping {file} due to the following error: {e}")
            continue

    documents_df = pd.concat(dfs, ignore_index=True)

    return documents_df


def process_docs(name, config, global_config, options):
    base = global_config.chatbot.data_dir / "sphinx"
    if not base.is_absolute():
        base = Path.cwd() / base

    repo_path = base / config.repo

    if options.anew:
        shutil.rmtree(repo_path)

    results = subprocess.run(
        here / "refresh-repo.sh",
        env={
            "BASE": base,
            "REPO": config.repo,
            "BRANCH": config.branch,
            "REQFILE": config.requirements,
            **os.environ,
        },
    )

    if results.returncode == 0:
        print("Chunking the documents...")

        # Docs in HTML format
        outdir = repo_path / config.output

        # URL that will be prefixed to all chunk links
        base_url = config.base_url

        # Parser to use, you can create one by inheriting from buster.parser.Parser
        parser = SphinxParser

        # Path to output CSV file
        output_csv = base / f"{name}.csv"

        # Create the chunks, returns a DataFrame
        documents_df = get_all_documents(outdir, base_url, parser)

        # The source column is used to easily filter/update the documents.
        # We could have mila-docs, slack-threads, office-hours, ...
        documents_df["source"] = name

        # Save the chunks
        documents_df.to_csv(output_csv, index=False)

        print("Generating the embeddings...")

        documents = pd.read_csv(output_csv)

        dm = DeepLakeDocumentsManager(
            vector_store_path=global_config.chatbot.buster["retriever_cfg"]["path"],
            overwrite=True,
        )
        dm.add(documents)


def main(global_config, config, options):
    for key, settings in config.items():
        process_docs(key, settings, global_config, options)
