import gc
from nltk import word_tokenize
from nltk.tokenize import sent_tokenize
import itertools

from wikipedia import wikipedia_content
import time
MAX_CONTEXT = 10


def clean_sentence(sentence):
    return " ".join(sentence.strip().split())


def make_header(string):
    if "." in string:
        return string
    return "== " + string + " =="


def is_header(sentence):
    return "== " in sentence


def separate_headers(sentence):
    split_str = "===" if "===" in sentence else "=="
    return [make_header(x) for x in filter(None, [s.strip() for s in sentence.split(split_str)])]


def pool_find_passages(args):
    return find_passages(*args)


def find_passages(title, search_words):
    content = wikipedia_content(title, True)

    if content == None:
        return []

    sentences = map(clean_sentence, sent_tokenize(content))

    sentences = list(itertools.chain.from_iterable(
        [separate_headers(s) for s in sentences]))

    latest_end_idx = 0
    passages = []

    for idx in range(0, len(sentences)):
        sentence = sentences[idx].lower()
        if is_header(sentence):
            continue

        matches = [w for w in search_words if " {0}".format(w) in sentence]

        if len(matches) > 0:
            start_idx = max(0, idx - MAX_CONTEXT)
            if start_idx < latest_end_idx:
                continue
            end_idx = min(idx + MAX_CONTEXT, len(sentences))
            latest_end_idx = end_idx
            passages.append({
                "title": title,
                "context": sentences[start_idx:end_idx],
                "matchIdx": idx - start_idx,
                "startIdx": start_idx,
                "endIdx": end_idx,
                "matches": matches
            })

    remove = ["startIdx", "endIdx"]

    return [{key: passage[key] for key in passage if key not in remove} for passage in passages]
