"""Make src tgt from e2e compositional
"""
import argparse
import os
import datetime

def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument(
        '-o', '--output_dir_name', help='output directory',
        default='/home/henrye/projects/clear_tasks/data')
    parser.add_argument('-i', '--input_file_names', nargs='*', help='')
    args = parser.parse_args()

    input_dir_root = os.path.dirname(args.input_file_names[0])
    datetime_stamp = datetime.datetime.now().strftime('%a%d%b_%H%M')
    output_dir_root = input_dir_root + '_' + datetime_stamp
    output_dir_name = os.path.join(args.output_dir_name, output_dir_root)
    os.mkdir(output_dir_name)

    for input_file_name in args.input_file_names:
        with open(input_file_name) as in_file:
            src = []
            tgt = []
            for line in in_file:
                # Not very robust but w/e, how would corey schafer open a tsv?
                _, src_raw, tgt_raw = line.split('\t')
                # We need an abritrary but consistent ordering, which the data
                # doesn't come with. TODO add an original-ordering option
                src.append(' '.join(sorted([
                    tok for tok in src_raw.split()
                    if not any(char in tok for char in ['[', ']'])
                ])))
                tgt.append(' '.join([
                    tok.lower() for tok in tgt_raw.split()
                    if not any(char in tok for char in ['[', ']'])
                ]))

        input_file_root = os.path.basename(
            os.path.splitext(input_file_name)[0])

        src_file_name = os.path.join(output_dir_name, input_file_root + '.src')
        with open(src_file_name, 'w') as out_file:
            out_file.write('\n'.join(src))
        tgt_file_name = os.path.join(output_dir_name, input_file_root + '.tgt')
        with open(tgt_file_name, 'w') as out_file:
            out_file.write('\n'.join(tgt))



if __name__ == '__main__':
    main()
