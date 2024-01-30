import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial

import pandas as pd
from grizzlaxy import bear, here
from hrepr import H
from markdown import markdown
from starbear import FeedbackQueue

from .cfg import config

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
    completion = config.buster_object.process_input(question)
    text = ""
    for token in completion.answer_generator:
        text += token
        dest.set(H.raw(markdown(text)))

    if completion.answer_relevant:
        src = format_sources(completion.matched_documents)
        dest.print(H.div["sources-list"](H.raw(markdown(src))))


@bear
async def chat(page):
    page.add_resources(here() / "style.css")

    input_queue = FeedbackQueue().wrap(
        # Produce the dictionary of form values as the event
        form=True,
        # pre is run in the browser immediately after the event is fired.
        # It disables the input box. `this` is the <form> element.
        pre="""
            let inp = this.querySelector('input');
            inp.setAttribute('disabled', '');
        """,
        # post is run once we have the answer from the server (the call to resolve
        # in the event loop below). It clears the input box, re-enables it, and
        # puts the focus in it.  `this` is the <form> element.
        post="""
            let inp = this.querySelector('input');
            inp.value = '';
            inp.removeAttribute('disabled');
            inp.focus();
        """,
    )

    page.print(
        H.div["chat-interface"](
            out := H.div["chat-output"](
                H.p(
                    "Welcome to the Mila cluster chatbot! Please use the input box "
                    "below to ask questions about the cluster."
                )
            ).autoid(),
            H.div["chat-form"](
                H.form(
                    H.input["chat-question"](
                        placeholder="Ask your question here",
                        name="question",
                        autocomplete="off",
                    ),
                    # Submitting the form (pressing enter in the input box) will
                    # push the form data in the input_queue.
                    onsubmit=input_queue,
                )
            ),
            H.div["credits"]("Created with ❤️ by @jerpint and @hadrienbertrand"),
        )
    )

    async for entry, resolve in input_queue:
        # Loop over events
        question = entry["question"]
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

        # Triggers the `post` code on the browser
        await resolve(True)


ROUTES = chat
