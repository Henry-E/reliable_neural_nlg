import argparse
import os
import re


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

    das_files = [i for i in args.input_file_names if '-conc_das' in i]
    text_files = [i for i in args.input_file_names if '-text' in i]
    names = [
        re.search(r"(.*)-conc_das.txt", os.path.basename(i)).group(1)
        for i in das_files
    ]
    first_processed = True
    examples = [[] for i in range(3,9)]
    for name in names:
        text_file_name = next(
            (i for i in text_files if name + '-text.txt' in i), None)
        if not text_file_name:
            print(f'no matching text file found for {name}')
            break
        with open(text_file_name) as in_file:
            tgts = [line.strip() for line in in_file]
        das_file_name = next((i for i in das_files if name + '-conc_das.txt' in i),
                             None)
        with open(das_file_name) as in_file:
            srcs = [convert_mr(line.strip()) for line in in_file]
            src_lens = [len(src.split()) for src in srcs]
        if first_processed:
            for k, i in enumerate(range(3,9)):
                print(srcs[src_lens.index(i)])
                DAs = srcs[src_lens.index(i)]
                DAs = ', '.join([da.replace('_',' ') for da in DAs.split()])
                examples[k].append(DAs)
            first_processed = False
        for k, i in enumerate(range(3,9)):
            examples[k].append(tgts[src_lens.index(i)])
            # print(f'{name}, {i}: {tgts[src_lens.index(i)]}')
    colour_mapping = {
        'slug': 'seqtoseq',
        'test': 'datadriven',
        'tuda': 'templates',
        'DAs': 'DAs',
    }
    names.insert(0, 'DAs')
    for example in examples:
        # print(f'\hline \multicolumn{{2}}{{l}}{{Num DAs {len(example[0].split(", "))}}} \\\\ \hline')
        print(f'\hline \\\\ \n\hline')
        for name, this in zip(names, example):
            if name in ['DAs']:
                continue
            # TODO map name to the command
            print(f'\\textcolor{{{colour_mapping[name]}}}{{\\symb{colour_mapping[name]} {this}}} \\\\')
    import ipdb; ipdb.set_trace()

if __name__ == '__main__':
    main()
