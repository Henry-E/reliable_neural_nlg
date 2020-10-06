import argparse
import os
from collections import defaultdict, Counter
import re
import pprint

from tqdm import tqdm
import match_surface_forms
from matplotlib import pyplot as plt
import matplotlib.ticker as mtick
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
        # Could use the walrus operator here
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

    # Here we find the lowest frequency phrase in train with a matching phrase
    # in slug or tgen.
    # import ipdb; ipdb.set_trace()
    slot_mapping = {
        'name_x-name': 'Name [ x-name ]',
        'eat_type_pub': 'Eat Type [ pub ]',
        'price_range_more_than_£30': 'Price Range [ more than £30 ]',
        'rating_5_out_of_5': 'Customer Rating [ 5 out of 5 ]',
        'near_x-near': 'Near [ x-near ]',
        'price_range_cheap': 'Price Range [ cheap ]',
        'food_english': 'Food [ english ]',
        'eat_type_coffee_shop': 'Eat Type [ coffee shop ]',
        'food_japanese': 'Food [ japanese ]',
        'price_range_less_than_£20': 'Price Range [ less than £20 ]',
        'rating_low': 'Customer Rating [ low ]',
        'area_riverside': 'Area [ riverside ]',
        'family_friendly_yes': 'Family Friendy [ yes ]',
        'food_french': 'Food [ french ]',
        'price_range_£20-25': 'Price Range [ £20-25 ]',
        'rating_high': 'Customer Rating [ high ]',
        'price_range_moderate': 'Price Range [ moderate ]',
        'family_friendly_no': 'Family Friendy [ no ]',
        'rating_average': 'Customer Rating [ average ]',
        'area_city_centre': 'Area [ city centre ]',
        'food_fast_food': 'Food [ fast food ]',
        'rating_3_out_of_5': 'Customer Rating [ 3 out of 5 ]',
        'eat_type_restaurant': 'Eat Type [ restaurant ]',
        'food_italian': 'Food [ italian ]',
        'price_range_high': 'Price Range [ high ]',
        'food_indian': 'Food [ indian ]',
        'rating_1_out_of_5': 'Customer Rating [ 1 out of 5 ]',
        'food_chinese': 'Food [ chinese ]',
    }

    # top_n = 5
    for slot in all_form_counts['train'].keys():
        # Only get bar labels which were used by tgen or slug2slug
        bar_labels = []
        most_common_phrases = [
            phrase
            for phrase, count in all_form_counts['train'][slot].most_common()
        ]
        for phrase in most_common_phrases:
            # TODO generalise from just tgen and slug
            if phrase in all_form_counts['slug'][slot].keys(
            ) or phrase in all_form_counts['tgen'][slot].keys(
            ) or phrase in all_form_counts['baseline'][slot].keys():
                bar_labels.append(phrase)

        # bar_labels = [
        #     phrase for phrase, count in all_form_counts['train']
        #     [slot].most_common(top_n)
        # ]
        bar_labels.append('remaining')
        # TODO think about how to order the names later
        all_heights = defaultdict(list)
        for name in names:
            total_count = sum(all_form_counts[name][slot].values())
            if total_count == 0:
                continue
            for phrase in bar_labels:
                all_heights[name].append((all_form_counts[name][slot][phrase] /
                                         total_count))
            # if name == 'train':
            total_visible = sum(all_heights[name])
            total_remaining = total_count - round(
                total_visible * total_count)
            if total_remaining > 0:
                # Count up how many unique phrases are missing, +1 for the
                # remaining label itself
                num_remaining_phrases = len(all_form_counts[name][slot]) - len(all_heights[name]) + 1
                all_heights[name][-1] = total_remaining / total_count
            # A quick hack to make heights into percentages
            for i, height in enumerate(all_heights[name][:]):
                all_heights[name][i] = height * 100

            # TODO add a special check to lookup the value of missing phrases
            # from the non-train datasets
        # gap = 0.8 / len(all_heights['train'])
        width = 1 / (len(all_heights) + 1)
        this_gap = width
        # import ipdb; ipdb.set_trace()
        name_mapping = {
            'slug': 'Slug2Slug',
            'tgen': 'TGen',
            'train': 'E2E Dataset',
        }
        ind =  np.arange(len(all_heights['train']))
        for i, (name, bar_heights) in enumerate(all_heights.items()):
            this_name = name_mapping[name]
            # another verbose hack to get a 'hatch' onto the train bar
            if name == 'train':
                plt.bar(ind + this_gap,
                        bar_heights,
                        width=width,
                        # color=color_list[i % len(color_list)],
                        color=plt.cm.Paired(i),
                        label=this_name,
                        hatch='/')
            else:
                plt.bar(ind + this_gap,
                        bar_heights,
                        width=width,
                        # color=color_list[i % len(color_list)],
                        color=plt.cm.Paired(i),
                        label=this_name)
            this_gap += width
        ax = plt.gca()
        # Two layers of params, bit messy https://stackoverflow.com/a/53199989/4507677
        grouping_ticks = np.arange(start=(-1/2)*width, stop=len(all_heights['train']), step=4*width)
        # grouping_ticks = np.append(
        #     grouping_ticks,
        #     np.arange(start=3 * width,
        #               stop=len(all_heights['train']),
        #               step=4 * width))
        ax.set_xticks(grouping_ticks + (1 / 2) * width)
        ax.set_xticklabels([])
        ax.tick_params(axis='x', which='major', length=5)
        # Then the ticks with the labels
        label_ticks =  np.arange(len(all_heights['train']))
        ax.set_xticks(label_ticks + 1 / 2, minor=True)
        # Counting up average of non-missing forms used
        num_slug_labels = 0
        for label, freq in zip(bar_labels, all_heights['slug']):
            if label == 'missing' or freq <= 0:
                continue
            num_slug_labels += 1
        num_tgen_labels = 0
        for label, freq in zip(bar_labels, all_heights['tgen']):
            if label == 'missing' or freq <= 0:
                continue
            num_tgen_labels += 1
        # Some issue with the total phrases from train here, but previous numbers still usable
        # print(num_slug_labels, num_tgen_labels, num_remaining_phrases + len(all_heights['train']) - 1)
        if 'missing' in bar_labels:
            idx = bar_labels.index('missing')
            bar_labels[idx] = '$\\mathbf{SF\, not\, found}$'
        if 'remaining' in bar_labels:
            idx = bar_labels.index('remaining')
            bar_labels[idx] = f'$\\mathbf{{{num_remaining_phrases}\, Remaining\, SFs}}$'
        # print(num_remaining_phrases)
        # import ipdb; ipdb.set_trace()
        ax.set_xticklabels(bar_labels, minor=True)
        if 4 < len(all_heights['train']):
            ax.tick_params(axis='x', which='minor', length=0, rotation=80)
        else:
            ax.tick_params(axis='x', which='minor', length=0, rotation=50)
        plt.legend()
        # plt.title(f"Frequency of Surface Forms for {slot_mapping[slot]}", fontsize='x-large')
        plt.title(f"{slot_mapping[slot]}", fontsize='x-large')
        # Percentages on the y-axis https://stackoverflow.com/a/36319915/4507677
        ax.yaxis.set_major_formatter(mtick.PercentFormatter())
        plt.ylabel('Frequency', fontsize='x-large')
        plt.xlabel('Surface Form (SF)', fontsize='x-large')
        # plt.style.use('fivethirtyeight')
        axes = plt.gca()
        # axes.set_xlim([xmin,xmax])
        axes.set_ylim([0, 100])
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
    # import ipdb; ipdb.set_trace()



if __name__ == '__main__':
    main()
