import argparse
import os
import re
import csv

from collections import defaultdict, Counter

from tqdm import tqdm

# TODO replace with joined da+value
REALIZATIONS = {
    'area_city_centre': [
        '(?:city|town) cent(?:re|er)',
        'cent(?:re|er) of (?:the )?(?:city|town)',
        'cent(?:re|er)',
    ],
    'area_riverside': [
        'river ?side',
        '(?:near|by|at|close to|along|on|off|beside) the river',
        '(?:banks|margin) of the river',
        'river(?:front)?',
    ],
    'eattype_coffee_shop': [
        'coffee[- ]+shop',
        'caf[eé]',
        'coffee',
    ],
    'eattype_pub': [
        'pub',
    ],
    'eattype_restaurant': [
        'restaurant',
    ],
    'familyfriendly_no': [
        '(?:isn\'t|not|non|no)[ -]+(?:\w+ ){0,2}(?:child|children|family|kids|kid)[ -]+(?:friendly|orien(?:ta)?ted)',
        '(?:child|children|family|kids|kid)[ -]+unfriendly',
        'adults?[ -]+only',
        'only for adults',
        'adults?',
        '(?:no|not) *a? *(?:kids|children|famil(?:y|ies))',
        '(?:not|no)(?: good| suitable| friendly| orien(?:ta)?ted| open(?:ed))? (?:at|for|to|with)(?: the)? (?:kids|children|family|families|all age)',
        '(?:kids?|child(?:ren)?|famil(?:y|ies)) (?:are|is)(?:n\'t| not) (?:welcome|allowed|accepted)',
        '(?:does not|doesn\'t) (?:welcome|allow|accept) (?:\w+ ){0,2}(?:kids?|child(?:ren)?|famil(?:y|ies)|all age)',
        'adult (?:establishment|venue|place|establish)',
    ],
    'familyfriendly_yes': [
        'for (?:kids|children|family|families)',
        'family place',
        'place to bring the(?: whole)? family',
        '(?:friendly|suitable|good|orien(?:ta)?ted|open(?:ed)) (?:at|with|to|for)(?: the)(?:kids?|child(?:ren)?|famil(?:y|ies)?|all age)',
        '(?:child|children|family|kids|kid)[ -]+(?:friendly|orien(?:ta)?ted)',
        '(?:kids?|child(?:ren)?|famil(?:y|ies)) (?:are|is) (?:welcome|allowed|accepted)',
        '(?:welcomes?|allows?|accepts?) (?:\w+ ){0,2}(?:kids?|child(?:ren)?|famil(?:y|ies)|all age)',
    ],
    'food_chinese': ['Chinese', 'Chines'],
    'food_english': ['English', 'British'],
    'food_fast_food': ['Fast food'],
    'food_french': ['French'],
    'food_indian': ['Indian'],
    'food_italian': ['Italian'],
    'food_japanese': ['Japanese'],
    'name': ['__name__'],
    'near': ['__near__'],
    "pricerange_cheap": [
        "(?:inexpensive|cheap)(?:ly)?",
        "low[- ]+price[ds]?",
        "affordabl[ey]",
        "prices?(?: range)?(?: \w+){0,3} low",
    ],
    "pricerange_less_than_£20": [
        "(?:inexpensive|cheap)(?:ly)?",
        "affordabl[ey]",
        "(?:less than|under) £? *20 *(?:pounds)?",
        "moderately priced",
        "low[- ]+price[ds]?",
        "prices?(?: range)?(?: \w+){0,3} low",
    ],
    "pricerange_more_than_£30": [
        "(?:more than|over|start at|higher than) *(?:£? *30|thirty pounds)",
        "high[- ]+price[ds]?",
        "expensive",
        "not cheap",
        "prices?(?: range)?(?: \w+){0,3} high",
    ],
    "pricerange_high": [
        "high[- ]+price[ds]?",
        "expensive",
        "prices?(?: range)?(?: \w+){0,3} high",
    ],
    "pricerange_moderate": [
        "(?:moderate|reasonable|ok|average)(?:ly)?[- ]+(price[ds]?|pricing)(?: *range)?",
        "not cheap",
        "affordable",
        "mid[- ]+(?:range[- ]+)price[ds]?",
        "prices?(?: range)?(?: \w+){0,3} (?:ok|average|moderate|reasonable)",
    ],
    "pricerange_£20-25": [
        "£? *20 *(?:[-–]*|to) *£? *25(?: pounds)?",
        "(?:moderate|reasonable|ok|average|mid)(?:ly)?[- ]+price[ds]?(?: *range)?",
        "prices?(?: range)?(?: \w+){0,3} (?:ok|average|moderate|reasonable)",
        "affordable",
    ],
    "customerrating_1_out_of_5": [
        "(?:1|one)(?:(?: out)? of (?:5|five)(?: stars?)?|[- ]+stars?)(?: rating)?",
        "(?:rat(?:ings?|e[ds]?)|reviews?|standards?|quality)(?: \w+){0,2} (?:as )?(?:low|bad|poor)(?:(?: \w+){0,3} (?:1|one)(?:(?: out)? of (?:5|five)|[- ]+stars?))?",
        "(?:low|bad|poor|(?:not|doesn't|isn't)(?: \w+){0,2} (:?good|well))(?:ly)?(?:[ -]+\w+){0,2}[ -]+(?:rat(?:ings?|ed)|reviews?|standards?|quality)(?:(?: \w+){0,3} (?:1|one)(?:(?: out)? of (?:5|five)(?: stars?)?|[- ]+stars?))?",
    ],
    "customerrating_3_out_of_5": [
        "(?:3|three)(?:(?: out)? of (?:5|five)(?: stars?)?|[- ]+stars?)(?: rating)?",
        "(?:rat(?:ings?|e[ds]?)|reviews?|standards?|quality)(?: \w+){0,2} (?:as )?average(?:(?: \w+){0,3} (?:3|three)(?:(?: out)? of (?:5|five)|[- ]+stars?))?",
        "(?:average|(?<!very )(?:good|well))(?:ly)?(?:[ -]+\w+){0,2}[ -]+(?:rat(?:ings?|ed)|reviews?|standards?|quality)(?:(?: \w+){0,3} (?:3|three)(?:(?: out)? of (?:5|five)(?: stars?)?|[- ]+stars?))?",
    ],
    "customerrating_5_out_of_5": [
        "(?:5|five)(?:(?: out)? of (?:5|five)(?: stars?)?|[- ]+stars?)(?: rating)?",
        "(?:rat(?:ings?|e[ds]?)|reviews?|standards?|quality)(?: \w+){0,2} (?:as )?high(?:(?: \w+){0,3} (?:5|five)(?:(?: out)? of (?:5|five)|[- ]+stars?))?",
        "(?:high|excellent|very good|great)(?:ly)?(?:[ -]+\w+){0,2}[ -]+(?:rat(?:ings?|ed)|reviews?|standards?|quality)(?:(?: \w+){0,3} (?:5|five)(?:(?: out)? of (?:5|five)(?: stars?)?|[- ]+stars?))?",
    ],
    "customerrating_high": [
        "(?:5|five)(?:(?: out)? of (?:5|five)(?: stars?)?|[- ]+stars?)(?: rating)?",
        "(?:rat(?:ings?|e[ds]?)|reviews?|standards?|quality)(?: \w+){0,2} (?:as )?high",
        "(?:high|excellent|very good|great|well)(?:ly)?(?:[ -]+\w+){0,2}[ -]+(?:rat(?:ings?|ed)|reviews?|standards?|quality)",
    ],
    "customerrating_average": [
        "(?:3|three)(?:(?: out)? of (?:5|five)(?: stars?)?|[- ]+stars?)(?: rating)?",
        "(?:rat(?:ings?|e[ds]?)|reviews?|standards?|quality)(?: \w+){0,2} (?:as )?average",
        "(?:average|(?<!very )(?:good|well))(?:ly)?(?:[ -]+\w+){0,2}[ -]+(?:rat(?:ings?|ed)|reviews?|standards?|quality)",
    ],
    "customerrating_low": [
        "(?:1|one)(?:(?: out)? of (?:5|five)(?: stars?)?|[- ]+stars?)(?: rating)?",
        "(?:rat(?:ings?|e[ds]?)|reviews?|standards?|quality)(?: \w+){0,2} (?:as )?(?:low|bad|poor)",
        "(?:low|bad|poor|(?:not|doesn't|isn't)(?: \w+){0,2} (?:well|good))(?:ly)?(?:[ -]+\w+){0,2}[ -]+(?:rat(?:ings?|ed)|reviews?|standards?|quality)",
    ],
}


def compile_patterns(patterns):
    """Compile a list of patterns into one big option regex. Note that all of them will match whole words only."""
    # pad intent patterns with \b (word boundary), unless they contain '^'/'$' (start/end)
    return re.compile('|'.join([((r'\b' if not pat.startswith(('^', '£')) else '') + pat +
                                 (r'\b' if not pat.endswith('$') else ''))
                                for pat in patterns]),
                      re.I | re.UNICODE)

# TODO change for sublooping, since there's only going to be depth=1
# TODO delete the capitalization stuff as well
# store "proper" capitalization of the values
# CAPITALIZE = {}
# compile realization patterns
for slot in REALIZATIONS.keys():
    # CAPITALIZE[slot] = {val.lower(): val for val in REALIZATIONS[slot]}
    REALIZATIONS[slot] = compile_patterns(REALIZATIONS[slot])
    # else:
    #     CAPITALIZE[slot] = {val.lower(): val for val in REALIZATIONS[slot].keys()}
    #     for value in REALIZATIONS[slot].keys():
    #         REALIZATIONS[slot][value] = compile_patterns(REALIZATIONS[slot][value])


class Match(object):
    """Realization pattern match in the system output"""

    def __init__(self, slot, value, regex_match):
        self.slot = slot
        self.value = value
        self._start = regex_match.start()
        self._end = regex_match.end()

    def is_same_string(self, other):
        return (self._start == other._start and self._end == other._end)

    def is_substring(self, other):
        return ((self._start > other._start and self._end <= other._end) or
                (self._start >= other._start and self._end < other._end))

    def __eq__(self, other):
        return (self.slot == other.slot and self.value == other.value and self.is_same_string(other))

    def __str__(self):
        return 'Match[%s=%s:%d-%d]' % (self.slot, self.value, self._start, self._end)

    def __repr__(self):
        return str(self)


# TODO delete reference to DA dicts and just use a list of da+values as the
# lookup in all situations
def reclassify_mr(ref, gold_mr):
    """Classify the MR given a text. Can use a gold-standard MR to make the classification more
    precise (in case of ambiguity, goes with the gold-standard value). Returns a dict-based MR format
    for the system output MR and the gold-standard MR."""
    # convert MR to dict for comparing & checking against
    # mr_dict = {}
    # for dai in gold_mr.dais:
    #     mr_dict[dai.slot] = mr_dict.get(dai.slot, {})
    #     val = CAPITALIZE[dai.slot][dai.value.lower()]
    #     mr_dict[dai.slot][val] = mr_dict[dai.slot].get(val, 0) + 1

    # create MR dict representation of the output text
    # first, collect all value matches
    matches = []
    # TODO change this to just looping over the gold mr list
    # for slot in REALIZATIONS.keys():
    for slot in gold_mr:
        # verbatim slot
        # if not isinstance(REALIZATIONS[slot], dict):
        matches.extend([Match(slot, slot, match)
                        for match in REALIZATIONS[slot].finditer(ref)])
        # slot with variable realizations
        # else:
        #     # collect all matches for all values
        #     for value in REALIZATIONS[slot].keys():
        #         matches.extend([Match(slot, CAPITALIZE[slot][value.lower()], match)
        #                         for match in REALIZATIONS[slot][value].finditer(ref)])

    # TODO I wonder if we need this if we don't have overlapping dialogue acts?
    # then filter out those that are substrings/duplicates (let only one value match,
    # preferrably the one indicated by the true MR -- check with the MR dict)
    # filt_matches = []
    # for match in matches:
    #     skip = False
    #     for other_match in matches:
    #         if match is other_match:
    #             continue
    #         if (match.is_substring(other_match) or
    #             (match.is_same_string(other_match) and
    #              (other_match.value in mr_dict.get(other_match.slot, {}).keys() or other_match in filt_matches))):
    #             skip = True
    #             break
    #     if not skip:
    #         filt_matches.append(match)

    # if filt_matches != matches:
    #     import ipdb; ipdb.set_trace()
    # now put it all into a dict
    surface_forms = {}
    # for match in filt_matches:
    for match in matches:
        surface_forms[match.slot] = ref[match._start:match._end]
    # print('missing from ref:', gold_mr - surface_forms.keys())
    # # print(sorted(gold_mr))
    # # print('added to ref', out_dict.keys() - mr_dict.keys())
    # [print(key, ':', value) for key, value in surface_forms.items()]
    # print(ref)
    # import ipdb; ipdb.set_trace()

    return surface_forms


def convert_mr(src_raw):
    """Convert the original src mr to the new style
    """
    src_toks = []
    for dialogue_act in src_raw.split(', '):
        value = dialogue_act[dialogue_act.find('[') + 1:dialogue_act.find(']')]
        value = value.replace(' ', '_').lower()
        slot = dialogue_act[0:dialogue_act.find('[')]
        slot = slot.replace(' ', '').lower()
        if any(i in slot for i in ['name', 'near']):
            src_toks.append(slot)
        else:
            src_toks.append('_'.join([slot, value]))
    return src_toks


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-o', '--output_dir_name', help='output directory')
    parser.add_argument('-i', '--input_file_names', nargs='*', help='')
    args = parser.parse_args()

    # We're not in the mood for specifying all the input files right now
    for input_file_name in args.input_file_names:
        # if 'surface_forms.json' in input_file_name:
        #     with open(input_file_name) as in_file:
        #         surface_forms = json.load(in_file)
        if '.src' in input_file_name:
            with open(input_file_name) as in_file:
                src_toks = [line.split() for line in in_file]
        elif any(i in input_file_name for i in ['.tgt', '.pred']):
            with open(input_file_name) as in_file:
                gen_text = [line.strip() for line in in_file]
        elif '.tsv' in input_file_name:
            with open(input_file_name) as in_file:
                csv_reader = csv.DictReader(in_file, delimiter='\t')
                src_toks = []
                gen_text = []
                for line in csv_reader:
                    src_toks.append(convert_mr(line['MR']))
                    gen_text.append(line['output'])


    form_count = defaultdict(Counter)
    for dialogue_acts, line in zip(tqdm(src_toks), gen_text):
        surface_forms = reclassify_mr(line, dialogue_acts)
        for key, value in surface_forms.items():
            form_count[key].update([value.strip()])
    [print(key, sum(value.values()), '\n', value.most_common(10)) for key,
            value in form_count.items() if len(value.most_common()) > 0]
    import ipdb; ipdb.set_trace()



if __name__ == '__main__':
    main()
