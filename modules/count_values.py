import argparse
import os
import json
from collections import defaultdict, Counter

from tqdm import tqdm

def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-o', '--output_dir_name', help='output directory')
    parser.add_argument('-i', '--input_file_names', nargs='*', help='')
    args = parser.parse_args()

    # We're not in the mood for specifying all the input files right now
    for input_file_name in args.input_file_names:
        if 'surface_forms.json' in input_file_name:
            with open(input_file_name) as in_file:
                surface_forms = json.load(in_file)
        elif '.src' in input_file_name:
            with open(input_file_name) as in_file:
                src_toks = [line.split() for line in in_file]
        elif any(i in input_file_name for i in ['.tgt', '.pred']):
            with open(input_file_name) as in_file:
                gen_text = [line.strip() for line in in_file]

    form_count = defaultdict(Counter)
    value_count = Counter()
    for dialoge_acts, line in zip(tqdm(src_toks), gen_text):
        for da_value in dialoge_acts:
            possible_forms = surface_forms[da_value]
            forms_found = [form for form in possible_forms if form in line]
            form_count[da_value].update(forms_found)
            value_count.update([da_value])

    for key, value in form_count.items():
        print(key, value_count[key])
        print(value.most_common(10))
    import ipdb; ipdb.set_trace()



if __name__ == '__main__':
    main()
