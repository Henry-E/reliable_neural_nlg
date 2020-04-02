"""Relex and detok single reference outputs from translate.py
"""
import argparse
import os
import re

from tqdm import tqdm
from sacremoses import MosesDetokenizer
from regex import Regex, UNICODE, IGNORECASE


class Detokenizer(object):
    """A simple de-tokenizer class.
    """

    def __init__(self):
        """Constructor (pre-compile all needed regexes).
        """
        # compile regexes
        self._currency_or_init_punct = Regex(r' ([\p{Sc}\(\[\{\¿\¡]+) ', flags=UNICODE)
        self._noprespace_punct = Regex(r' ([\,\.\?\!\:\;\\\%\}\]\)]+) ', flags=UNICODE)
        self._contract = Regex(r" (\p{Alpha}+) ' (ll|ve|re|[dsmt])(?= )", flags=UNICODE | IGNORECASE)
        self._dash_fixes = Regex(r" (\p{Alpha}+|£ [0-9]+) - (priced|star|friendly|(?:£ )?[0-9]+) ", flags=UNICODE | IGNORECASE)
        self._dash_fixes2 = Regex(r" (non) - ([\p{Alpha}-]+) ", flags=UNICODE | IGNORECASE)
        self._contractions = Regex(r" (n't)", flags=UNICODE)
        self._esses = Regex(r" s ", flags=UNICODE)
        self._international_things = {'chinese': 'Chinese', 'japanese':'Japanese',
                                      'french':'French', 'indian':'Indian',
                                      'english':'English', 'italian':'Italian'}
        self.moses_detokenizer = MosesDetokenizer()

    def detokenize(self, text):
        """Detokenize the given text.
        """
        text = ' ' + text + ' '
        text = self._dash_fixes.sub(r' \1-\2 ', text)
        text = self._dash_fixes2.sub(r' \1-\2 ', text)
        text = self._currency_or_init_punct.sub(r' \1', text)
        text = self._noprespace_punct.sub(r'\1 ', text)
        text = self._contract.sub(r" \1'\2", text)
        # TODO figure out why neither of the contraction replacements are working?
        text = self._contractions.sub(r"\1", text)
        text = text.replace(" n't", "n't")
        # if "n't" in text:
        #     import ipdb; ipdb.set_trace()
        text = self._esses.sub(r"s ", text)
        text = self.moses_detokenizer.detokenize(text.split())
        text = text.strip()
        # capitalize
        if not text:
            return ''
        return text

    def truecase(self, text):
        text = text.strip()
        for word, capitalised_word in self._international_things.items():
            text = text.replace(word, capitalised_word)
        if not text:
            return ''
        # there can be multiple sentences, we could use regex \. [a-z] but too
        # complicated to do the replace stuff
        sents = text.split('. ')
        sents = [sent[0].upper() + sent[1:] for sent in sents]
        text = '. '.join(sents)
        # text = text[0].upper() + text[1:]
        return text


def get_name_and_near(da):
    """Make a dict containing the lexicalised name and near slots

    We figure that a dict will be easier to do substitution with
    """
    name_and_near = {}
    for dialogue_act in da.split('&inform'):
        slot = dialogue_act[dialogue_act.find('(')+1:dialogue_act.find('=')]
        value = dialogue_act[dialogue_act.find('=')+1:dialogue_act.find(')')]
        value = value.replace("'","")
        if slot in ['name', 'near']:
            name_and_near['X-' + slot] = value
    return name_and_near


def main():
    """open predicted text file, then relexicalise and detokenize it using the
    lexicalised dialogue acts from tgen
    """
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-o', '--output_dir_name', help='output directory')
    parser.add_argument('-i', '--input_file_names', nargs='*', help='')
    args = parser.parse_args()

    if 2 < len(args.input_file_names):
        print('too many files')
        return

    # import ipdb; ipdb.set_trace()
    # predictions
    preds_file_name = [i for i in args.input_file_names if 'pred.txt' in i][0]

    # dialogue acts - conc means lexicalised
    das_file_name = [i for i in args.input_file_names
                     if '-conc_das.txt' in i][0]

    with open(preds_file_name) as in_file:
        preds = [line.strip() for line in in_file]
    with open(das_file_name) as in_file:
        das = [line.strip() for line in in_file]
        name_and_nears = [get_name_and_near(da) for da in das]

    detok = Detokenizer()
    pred_formatted = []
    for pred, name_and_near in zip(tqdm(preds), name_and_nears):
        # Make sense to relex before detok because of weird X-near/name tokens
        pred_relex = pred
        for key, value in name_and_near.items():
            pred_relex = pred_relex.replace(key, value)
        pred_detok = detok.detokenize(pred_relex)
        # TODO why isn't detok handling contractions properly?
        pred_detok = pred_detok.replace(" n't", "n't")
        pred_truecase = detok.truecase(pred_detok)
        pred_formatted.append(pred_truecase)
    # import ipdb; ipdb.set_trace()

    # Different approach to getting root because there's extra info in filenames
    input_file_root = os.path.basename(das_file_name).split('-')[0]
    output_file_root = input_file_root + '-eval.txt'
    output_file_name = os.path.join(args.output_dir_name, output_file_root)
    with open(output_file_name, 'w') as out_file:
        out_file.write('\n'.join(pred_formatted))


if __name__ == '__main__':
    main()
