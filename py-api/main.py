from typing import Optional
import spacy
from spacy.lang.nl.stop_words import STOP_WORDS
from string import punctuation
from heapq import nlargest
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.options("/summary")
def read_root():
    return {"Hello": "World"}


@app.get("/")
def read_root():
    return {"Hello": "World"}


class Article(BaseModel):
    text: str


@app.post("/summary")
def getSummary(article: Article):
    return summarize(article.text)


stopwords = list(STOP_WORDS)


nlp = spacy.load('nl_core_news_lg')


def readingTime(docs):
    total_words_tokens = [token.text for token in nlp(docs)]
    estimatedtime = len(total_words_tokens)/200
    return round(estimatedtime)


def summarize(articleText):
    docx = nlp(articleText)
    mytokens = [token.text for token in docx]
    word_frequencies = {}
    for word in docx:
        if word.text not in stopwords:
            if word.text not in word_frequencies.keys():
                word_frequencies[word.text] = 1
            else:
                word_frequencies[word.text] += 1
    maximum_frequency = max(word_frequencies.values())

    maximum_frequency = max(word_frequencies.values())

    for word in word_frequencies.keys():
        word_frequencies[word] = (word_frequencies[word]/maximum_frequency)

    sentence_list = [sentence for sentence in docx.sents]
    sentence_scores = {}
    for sent in sentence_list:
        for word in sent:
            if word.text.lower() in word_frequencies.keys():
                if len(sent.text.split(' ')) < 30:
                    if sent not in sentence_scores.keys():
                        sentence_scores[sent] = word_frequencies[word.text.lower()]
                    else:
                        sentence_scores[sent] += word_frequencies[word.text.lower()]

    summarized_sentences = nlargest(
        5, sentence_scores, key=sentence_scores.get)
    final_sentences = [w.text for w in summarized_sentences]
    summary = ' '.join(final_sentences)

    return {
        "summary": summary,
        "readingTimeOriginal": readingTime(articleText),
        "readingTimeSummary": readingTime(summary)
    }
