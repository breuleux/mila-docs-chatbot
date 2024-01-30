from functools import cached_property
from pathlib import Path
from gifnoc import define
from dataclasses import dataclass


@dataclass
class AcquireConfiguration:
    repo: str
    branch: str
    requirements: str
    output: str
    base_url: str


@dataclass
class ChatbotConfiguration:
    data_dir: Path
    acquire: dict[str, dict[str, AcquireConfiguration]]
    buster: dict

    @cached_property
    def buster_object(self):
        from buster.busterbot import Buster, BusterConfig
        from buster.completers import ChatGPTCompleter, DocumentAnswerer
        from buster.formatters.documents import DocumentsFormatterHTML
        from buster.formatters.prompts import PromptFormatter
        from buster.retriever import DeepLakeRetriever, Retriever
        from buster.tokenizers import GPTTokenizer
        from buster.validators import Validator

        buster_cfg = BusterConfig(**self.buster)

        retriever: Retriever = DeepLakeRetriever(**buster_cfg.retriever_cfg)
        tokenizer = GPTTokenizer(**buster_cfg.tokenizer_cfg)
        document_answerer: DocumentAnswerer = DocumentAnswerer(
            completer=ChatGPTCompleter(**buster_cfg.completion_cfg),
            documents_formatter=DocumentsFormatterHTML(tokenizer=tokenizer, **buster_cfg.documents_formatter_cfg),
            prompt_formatter=PromptFormatter(tokenizer=tokenizer, **buster_cfg.prompt_formatter_cfg),
            **buster_cfg.documents_answerer_cfg,
        )
        validator: Validator = Validator(**buster_cfg.validator_cfg)
        return Buster(retriever=retriever, document_answerer=document_answerer, validator=validator)


@dataclass
class OpenAIConfiguration:
    api_key: str


config = define(
    field="chatbot",
    model=ChatbotConfiguration,
)

oconfig = define(
    field="openai",
    model=OpenAIConfiguration,
    environ={"OPENAI_API_KEY": "api_key"},
)
