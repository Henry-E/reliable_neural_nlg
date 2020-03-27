import argparse
import os
from collections import defaultdict, Counter
import json

from tqdm import tqdm

def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument(
        '-o', '--output_dir_name', help='output directory',
        default='/home/henrye/projects/clear_tasks/misc')
    parser.add_argument('-i', '--input_file_name', help='training set')
    args = parser.parse_args()

    with open(args.input_file_name) as in_file:
        tgts = []
        for line in in_file:
            _, _, tgt = line.split('\t')
            tgts.append(tgt.split())

    surface_forms = defaultdict(list)
    form_count = defaultdict(Counter)
    has_arg = False
    for tgt in tqdm(tgts):
        for tok in tgt:
            if '[__ARG_' in tok:
                has_arg = True
                # eg. '[__ARG_PRICERANGE_MORE_THAN__'
                current_arg = tok[7:-2].lower()
                surface_forms[current_arg].append([])
                continue
            if ']' in tok and has_arg:
                has_arg = False
                full_phrase = ' '.join(surface_forms[current_arg][-1])
                form_count[current_arg].update([full_phrase])
                continue
            if has_arg:
                surface_forms[current_arg][-1].append(tok.lower())
    out_surface_forms = {}
    for key, value in surface_forms.items():
        out_surface_forms[key] = list(set(' '.join(i) for i in value))
    # save the possible surface forms
    output_file_name = os.path.join(args.output_dir_name, 'surface_forms.json')
    with open(output_file_name, 'w') as out_file:
        json.dump(
            out_surface_forms, out_file, sort_keys=True, indent=4,
            ensure_ascii=False)
    # save the forms count
    output_file_name = os.path.join(args.output_dir_name, 'form_count.json')
    with open(output_file_name, 'w') as out_file:
        json.dump(
            form_count, out_file, sort_keys=True, indent=4,
            ensure_ascii=False)
    # save the most common 10 to make it more readable
    output_file_name = os.path.join(args.output_dir_name, 'most_common_forms.txt')
    with open(output_file_name, 'w') as out_file:
        for key, value in form_count.items():
            print(key, sum(value.values()), file=out_file)
            print(value.most_common(10), file=out_file)


if __name__ == '__main__':
    main()
