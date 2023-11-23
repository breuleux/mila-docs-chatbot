import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial

import pandas as pd
from grizzlaxy import bear, here
from hrepr import H
from markdown import markdown
from starbear import Queue

from . import cfg

pool = ThreadPoolExecutor(max_workers=5)


def format_sources(matched_documents: pd.DataFrame) -> str:
    if len(matched_documents) == 0:
        return ""

    matched_documents.similarity_to_answer = matched_documents.similarity_to_answer * 100

    documents_answer_template: str = (
        "📝 Here are the sources I used to answer your question:\n\n{documents}\n\n{footnote}"
    )
    document_template: str = "* [🔗 {document.title}]({document.url}), relevance: {document.similarity_to_answer:2.1f} %"

    documents = "\n".join([document_template.format(document=document) for _, document in matched_documents.iterrows()])
    footnote: str = "I'm a bot 🤖 and not always perfect."

    return documents_answer_template.format(documents=documents, footnote=footnote)


def complete(dest, question):
    completion = cfg.buster.process_input(question)
    text = ""
    for token in completion.answer_generator:
        text += token
        dest.set(H.raw(markdown(text)))

    if completion.answer_relevant:
        src = format_sources(completion.matched_documents)
        dest.print(H.div["sources-list"](H.raw(markdown(src))))


@bear
async def chat(page):
    def set_form():
        form = H.form(
            inp := H.input["chat-question"](
                placeholder="Ask your question here",
                name="question",
                autocomplete="off",
            ).autoid(),
            onsubmit=q.wrap(form=True),
        )
        page[form_container].set(form)
        page[inp].do("this.focus()")

    page["head"].print(H.link(rel="stylesheet", href=here() / "style.css"))
    q = Queue()
    page.print(
        H.div["chat-interface"](
            out := H.div["chat-output"](
                H.p(
                    "Welcome to the Mila cluster chatbot! Please use the input box "
                    "below to ask questions about the cluster."
                )
            ).autoid(),
            form_container := H.div["chat-form"]().autoid(),
            H.div["credits"]("Created with ❤️ by @jerpint and @hadrienbertrand"),
        )
    )
    set_form()

    async for entry in q:
        question = entry["question"]
        page[form_container].set(H.div["blocker-overlay"](question))
        page[out].print(
            H.div["chat-exchange"](
                H.div["log-question"](H.span["name"]("You"), H.raw(markdown(question))),
                reply := H.div["log-bot-reply"](
                    H.span["name"]("Buster"),
                    H.img["wait"](src=here() / "three-dots.svg"),
                ).autoid(),
            ),
            method="afterbegin",
        )

        await asyncio.wrap_future(
            pool.submit(partial(complete, page[reply], question)),
        )
        set_form()


ROUTES = chat
