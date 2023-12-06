import logging
import os

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

buster = None
config: dict = None


def configure(cfg):
    global config, buster
    config = cfg

    # set openAI creds
    os.environ["OPENAI_API_KEY"] = config["openai_api_key"]

    from buster.busterbot import Buster, BusterConfig
    from buster.completers import ChatGPTCompleter, DocumentAnswerer
    from buster.formatters.documents import DocumentsFormatterHTML
    from buster.formatters.prompts import PromptFormatter
    from buster.retriever import DeepLakeRetriever, Retriever
    from buster.tokenizers import GPTTokenizer
    from buster.validators import Validator

    buster_cfg = BusterConfig(**cfg["buster"])

    # initialize buster with the config in cfg.py (adapt to your needs) ...
    retriever: Retriever = DeepLakeRetriever(**buster_cfg.retriever_cfg)
    tokenizer = GPTTokenizer(**buster_cfg.tokenizer_cfg)
    document_answerer: DocumentAnswerer = DocumentAnswerer(
        completer=ChatGPTCompleter(**buster_cfg.completion_cfg),
        documents_formatter=DocumentsFormatterHTML(tokenizer=tokenizer, **buster_cfg.documents_formatter_cfg),
        prompt_formatter=PromptFormatter(tokenizer=tokenizer, **buster_cfg.prompt_formatter_cfg),
        **buster_cfg.documents_answerer_cfg,
    )
    validator: Validator = Validator(**buster_cfg.validator_cfg)
    buster = Buster(retriever=retriever, document_answerer=document_answerer, validator=validator)
