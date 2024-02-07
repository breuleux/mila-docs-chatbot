import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial

import pandas as pd
from grizzlaxy import bear, here
from hrepr import H
from markdown import markdown
from starbear import FeedbackQueue

from ..config import config

pool = ThreadPoolExecutor(max_workers=5)


def format_sources(matched_documents: pd.DataFrame):
    if len(matched_documents) == 0:
        return ""

    matched_documents.similarity_to_answer = matched_documents.similarity_to_answer * 100

    return H.div["sources-list"](
        "📝 Here are the sources I used to answer your question:",
        H.ul(
            H.li(
                H.a(document.title, href=document.url, target="_blank"),
                f", relevance: {document.similarity_to_answer:2.1f} %",
            )
            for _, document in matched_documents.iterrows()
        ),
        "I'm a bot 🤖 and not always perfect.",
    )


def complete(dest, question):
    completion = config.buster_object.process_input(question)
    text = ""
    for token in completion.answer_generator:
        text += token
        dest.set(H.raw(markdown(text)))

    if completion.answer_relevant:
        dest.print(format_sources(completion.matched_documents))


@bear(template_params={"title": "Mila documentation chatbot"})
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
            out := H.div["chat-output"](H.p(config.strings.welcome)).autoid(),
            H.div["chat-form"](
                H.form(
                    H.input["chat-question"](
                        placeholder=config.strings.placeholder,
                        name="question",
                        autocomplete="off",
                    ),
                    # Submitting the form (pressing enter in the input box) will
                    # push the form data in the input_queue.
                    onsubmit=input_queue,
                )
            ),
            H.div["credits"](config.strings.credits),
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
