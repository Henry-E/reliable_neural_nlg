src_file="test"
model_file_name="/home/henrye/projects/clear_tasks/experiments/train/final_baseline_Mon18May_1005/final_baseline_step_3600.pt"
src_file_name="/home/henrye/projects/clear_tasks/data/baseline_Mon18May_0934/${src_file}.src"
translate_dir_name="/home/henrye/projects/clear_tasks/experiments/translate/${src_file}_baseline_$(date '+%a%d%b_%H%M')"
mkdir -p "$translate_dir_name"
echo "Translating to ${translate_dir_name}"

python /home/henrye/downloads/surface_realization_opennmt-py/translate.py \
    -model "$model_file_name" \
    -src "$src_file_name" \
    -dynamic_dict \
    -share_vocab \
    -replace_unk \
    -output "$translate_dir_name"/"$src_file".pred.txt \
    -batch_size 1 \
    -gpu 0

relex_and_detok_dir_name="/home/henrye/projects/clear_tasks/experiments/relex_and_detok/${src_file}_baseline_$(date '+%a%d%b_%H%M')"
mkdir -p "$relex_and_detok_dir_name"
echo "Relexing to ${relex_and_detok_dir_name}"

python modules/relex_and_detok.py \
    -i /home/henrye/downloads/tgen/e2e-challenge/input/${src_file}-conc_das.txt \
        "$translate_dir_name"/"$src_file".pred.txt \
    -o "$relex_and_detok_dir_name"

echo "Slot error calculation"

cd /home/henrye/downloads/e2e-cleaning/
./slot_error.py \
    -m ../tgen/e2e-challenge/input/${src_file}-conc_das.txt "$relex_and_detok_dir_name"/${src_file}-eval.txt
cd /home/henrye/projects/clear_tasks/

echo "Use this command to get bleu scores"

echo "python ~/downloads/e2e-metrics/measure_scores.py /home/henrye/downloads/tgen/e2e-challenge/input/${src_file}-conc.txt ${relex_and_detok_dir_name}/${src_file}-eval.txt"
