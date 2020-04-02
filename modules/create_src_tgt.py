"""Create src tgt files from delex e2e - delexed by tgen
"""
import argparse
import os
import datetime
from collections import defaultdict, Counter

from tqdm import tqdm
import match_surface_forms


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


def create_src_tgt(input_file_names, output_dir_name, experiment, debug=False):
    """split out the src and tgt logic

    This way we can do train, dev etc. all in one call
    """
    srcs = []
    tgts = []
    for input_file_name in input_file_names:
        if '-text.txt' in input_file_name:
            with open(input_file_name) as in_file:
                tgts = [line.strip() for line in in_file]
        elif '-das.txt' in input_file_name:
            with open(input_file_name) as in_file:
                srcs = [convert_mr(line.strip()) for line in in_file]


    form_count = defaultdict(Counter)
    if experiment in ['surface_forms']:
        new_srcs = []
        for src, tgt in zip(tqdm(srcs), tgts):
            # TODO effect of leaving out 'missing' slots
            # TODO effect of slots in order they appear in sent
            # TODO some fix for overlapping values
            surface_forms = match_surface_forms.match_surface_forms(
                tgt, src.split())
            new_src = ' '.join([k + ' ' + v for k, v in surface_forms.items()])
            new_srcs.append(new_src)
            for key, value in surface_forms.items():
                if value in ['missing']:
                    continue
                form_count[key].update([value.strip()])
        srcs = new_srcs

    if debug:
        return form_count

    # We only create the output dir here in case something else messes up
    # earlier and we don't want too many dirs clogging up the place
    if not os.path.exists(output_dir_name):
        os.mkdir(output_dir_name)

    input_file_root = os.path.basename(os.path.splitext(input_file_name)[0])
    input_file_root = input_file_root[:input_file_root.find('-')]

    src_file_name = os.path.join(output_dir_name, input_file_root + '.src')
    with open(src_file_name, 'w') as out_file:
        out_file.write('\n'.join(srcs))
    tgt_file_name = os.path.join(output_dir_name, input_file_root + '.tgt')
    with open(tgt_file_name, 'w') as out_file:
        out_file.write('\n'.join(tgts))

    return form_count


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument(
        '-o', '--output_dir_name', help='output directory',
        default='/home/henrye/projects/clear_tasks/data')
    parser.add_argument(
        '-i', '--input_file_names', nargs='*',
        help='files from tgen/e2e/input, one train/dev/test set at a time')
    parser.add_argument('--experiment',
                        choices=['baseline', 'surface_forms'],
                        default='baseline')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    datetime_stamp = datetime.datetime.now().strftime('%a%d%b_%H%M')
    output_dir_root = '_'.join([args.experiment, datetime_stamp])
    output_dir_name = os.path.join(args.output_dir_name, output_dir_root)

    train_file_names = [i for i in args.input_file_names if 'train' in i]
    valid_file_names = [
        i for i in args.input_file_names if 'valid_single_ref' in i
    ]

    form_count = create_src_tgt(train_file_names, output_dir_name,
                                args.experiment, args.debug)
    _ = create_src_tgt(valid_file_names, output_dir_name, args.experiment,
                       args.debug)
    # dev-conc.txt is the tgt when running measure_scores.py
    dev_file_name = [i for i in args.input_file_names if 'dev-das.txt' in i][0]
    if dev_file_name:
        with open(dev_file_name) as in_file:
            srcs = [convert_mr(line.strip()) for line in in_file]
        if args.experiment in ['surface_forms']:
            new_srcs = []
            for src in srcs:
                new_src = []
                for slot in src.split():
                    if slot in [
                            'price_range_cheap', 'price_range_moderate',
                            'area_city_centre',
                    ]:
                        value = form_count[slot].most_common(2)[1][0]
                    elif slot in [
                            'price_range_less_than_£20',
                            'price_range_more_than_£30',
                    ]:
                        value = form_count[slot].most_common(3)[2][0]
                    else:
                        value = form_count[slot].most_common(1)[0][0]
                    new_src.extend([slot, value])
                new_srcs.append(' '.join(new_src))
            srcs = new_srcs
        if args.debug:
            return
        src_file_name = os.path.join(output_dir_name, 'dev.src')
        with open(src_file_name, 'w') as out_file:
            out_file.write('\n'.join(srcs))
    # if we had to do this more than twice we would put it in a function
    # test_file_name = [i for i in args.input_file_names if 'test-das.txt' in i]
    # if test_file_name:
    #     with open(test_file_name) as in_file:
    #         src = [convert_mr(line.strip()) for line in in_file]
    #     src_file_name = os.path.join(output_dir_name, 'test.src')
    #     with open(src_file_name, 'w') as out_file:
    #         out_file.write('\n'.join(src))


if __name__ == '__main__':
    main()
