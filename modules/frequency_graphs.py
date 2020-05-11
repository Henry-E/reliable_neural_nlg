import argparse
import os
from collections import defaultdict, Counter
import re
import pprint

from tqdm import tqdm
import match_surface_forms
from matplotlib import pyplot as plt
import numpy as np


def convert_mr(src_raw):
    """Convert the tgen mr to the new style

    it's in an annoying format
    inform(name=X-name)&inform(area='city centre')&inform(family_friendly=no)&inform(near=X-near)
    """
    src_toks = []
    for dialogue_act in src_raw.split('&inform'):
        slot = dialogue_act[dialogue_act.find('(')+1:dialogue_act.find('=')]
        value = dialogue_act[dialogue_act.find('=')+1:dialogue_act.find(')')]
        value = value.replace(' ', '_').replace("'","").lower()
        src_toks.append('_'.join([slot, value]))
    return ' '.join(src_toks)


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-o', '--output_dir_name', help='output directory')
    parser.add_argument('-i', '--input_file_names', nargs='*', help='')
    args = parser.parse_args()

    das_files = [i for i in args.input_file_names if '-das' in i]
    text_files = [i for i in args.input_file_names if '-text' in i]
    names = [
        re.search(r"(.*)-das.txt", os.path.basename(i)).group(1)
        for i in das_files
    ]
    all_form_counts = defaultdict(lambda: defaultdict(Counter))
    for name in names:
        text_file_name = next(
            (i for i in text_files if name + '-text.txt' in i), None)
        if not text_file_name:
            print(f'no matching text file found for {name}')
            break
        with open(text_file_name) as in_file:
            tgts = [line.strip() for line in in_file]
        das_file_name = next((i for i in das_files if name + '-das.txt' in i),
                             None)
        with open(das_file_name) as in_file:
            srcs = [convert_mr(line.strip()) for line in in_file]
        for src, tgt in zip(tqdm(srcs), tgts):
            surface_forms = match_surface_forms.match_surface_forms(
                tgt, src.split())
            for slot, value in surface_forms.items():
                all_form_counts[name][slot].update([value.strip()])

    top_n = 5
    for slot in all_form_counts['train'].keys():
        bar_labels = [
            phrase for phrase, count in all_form_counts['train']
            [slot].most_common(top_n)
        ]
        bar_labels.append('remaining')
        # TODO think about how to order the names later
        all_heights = defaultdict(list)
        for name in names:
            total_count = sum(all_form_counts[name][slot].values())
            if total_count == 0:
                continue
            for phrase in bar_labels:
                all_heights[name].append(all_form_counts[name][slot][phrase] /
                                         total_count)
            # if name == 'train':
            total_visible = sum(all_heights[name])
            total_remaining = total_count - round(
                total_visible * total_count)
            if total_remaining > 0:
                all_heights[name][-1] = total_remaining / total_count
            # TODO add a special check to lookup the value of missing phrases
            # from the non-train datasets
        gap = 0.8 / len(all_heights['train'])
        # import ipdb; ipdb.set_trace()
        for i, (name, bar_heights) in enumerate(all_heights.items()):
            X = np.arange(len(bar_heights))
            plt.bar(X + i * gap,
                    bar_heights,
                    width=gap,
                    # color=color_list[i % len(color_list)],
                    color=plt.cm.Paired(i),
                    label=name)
        plt.xticks(np.arange(len(all_heights['train'])), bar_labels)
        plt.tick_params(axis='x', rotation=50)
        plt.legend()
        plt.tight_layout()
        plt.savefig(f'/home/henrye/projects/clear_tasks/experiments/frequency_graphs/{slot}.png', c='k')
        print(f'{slot}')
        plt.clf()


    # # slot = 'rating_3_out_of_5'
    # total = sum(all_form_counts[name][slot].values())
    # bar_heights = []
    # bar_labels = []
    # visible_total = 0
    # for phrase, count in all_form_counts[name][slot].most_common(5):
    #     visible_total += count
    #     bar_heights.append(round(count/total, 3))
    #     bar_labels.append(phrase)
    # bar_labels.append('remaining')
    # bar_heights.append((total - visible_total) / total)

    # tgen_total = sum(all_form_counts[slot]['tgen'].values())
    # tgen_heights = []
    # for phrase, _ in all_form_counts[name][slot].most_common(5):
    #     tgen_heights.append(
    #         round(all_form_counts[slot]['tgen'][phrase] / tgen_total))
    # # for phrase in all_form_counts['area_riverside']['tgen'].keys():
    # all_heights = {
    #     'train': bar_heights,
    #     'tgen': tgen_heights,
    # }


    # for name in all_form_counts[slot].keys():
    #     if name == 'train':
    #         continue


    # plt.bar(bar_labels, bar_heights)
    # plt.bar(bar_labels, tgen_heights)
    # plt.plot(x,y)
    import ipdb; ipdb.set_trace()



if __name__ == '__main__':
    main()
