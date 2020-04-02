model_file_name="/home/henrye/projects/clear_tasks/experiments/train/surface_forms_02Apr_1117/sf_step_4000.pt"
src_file_name="/home/henrye/projects/clear_tasks/data/surface_forms_Thu02Apr_1232/dev.src"
translate_dir_name="/home/henrye/projects/clear_tasks/experiments/translate/surface_forms_02Apr_1234"
python /home/henrye/downloads/OpenNMT-py/translate.py \
    -model "$model_file_name" \
    -src "$src_file_name" \
    -dynamic_dict \
    -share_vocab \
    -replace_unk \
    -output "$translate_dir_name"/pred.txt \
    -gpu 0

