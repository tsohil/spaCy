# coding: utf8
from __future__ import unicode_literals, division, print_function

import json
from ...gold import read_json_file, merge_sents
from ... import util


def conllu2json(input_path, output_path, n_sents=10, use_morphology=False):
    """Convert conllu files into JSON format for use with train cli.
    use_morphology parameter enables appending morphology to tags, which is
    useful for languages such as Spanish, where UD tags are not so rich.
    """
    # by @dvsrepo, via #11 explosion/spacy-dev-resources

    docs = []
    sentences = []
    conll_tuples = read_conllx(input_path, use_morphology=use_morphology)

    for i, (raw_text, tokens) in enumerate(conll_tuples):
        sentence, brackets = tokens[0]
        sentences.append(generate_sentence(sentence))
        # Real-sized documents could be extracted using the comments on the
        # conluu document
        if(len(sentences) % n_sents == 0):
            doc = create_doc(sentences, i)
            docs.append(doc)
            sentences = []

    output_filename = input_path.parts[-1].replace(".conllu", ".json")
    output_file = output_path / output_filename
    json.dump(docs, output_file.open('w', encoding='utf-8'), indent=2)
    util.print_msg("Created {} documents".format(len(docs)),
                   title="Generated output file {}".format(output_file))


def read_conllx(input_path, use_morphology=False, n=0):
    text = input_path.open('r', encoding='utf-8').read()
    i = 0
    for sent in text.strip().split('\n\n'):
        lines = sent.strip().split('\n')
        if lines:
            while lines[0].startswith('#'):
                lines.pop(0)
            tokens = []
            for line in lines:

                id_, word, lemma, pos, tag, morph, head, dep, _1, \
                _2 = line.split('\t')
                if '-' in id_ or '.' in id_:
                    continue
                try:
                    id_ = int(id_) - 1
                    head = (int(head) - 1) if head != '0' else id_
                    dep = 'ROOT' if dep == 'root' else dep
                    tag = pos+'__'+morph  if use_morphology else pos
                    tokens.append((id_, word, tag, head, dep, 'O'))
                except:
                    print(line)
                    raise
            tuples = [list(t) for t in zip(*tokens)]
            yield (None, [[tuples, []]])
            i += 1
            if n >= 1 and i >= n:
                break


def generate_sentence(sent):
    (id_, word, tag, head, dep, _) = sent
    sentence = {}
    tokens = []
    for i, id in enumerate(id_):
        token = {}
        token["orth"] = word[id]
        token["tag"] = tag[id]
        token["head"] = head[id] - i
        token["dep"] = dep[id]
        tokens.append(token)
    sentence["tokens"] = tokens
    return sentence


def create_doc(sentences,id):
    doc = {}
    paragraph = {}
    doc["id"] = id
    doc["paragraphs"] = []
    paragraph["sentences"] = sentences
    doc["paragraphs"].append(paragraph)
    return doc
