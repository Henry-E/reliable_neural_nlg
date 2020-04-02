python ~/downloads/OpenNMT-py/preprocess.py \
    -train_src /home/henrye/projects/clear_tasks/data/surface_forms_Thu02Apr_1025/train.src \
    -train_tgt /home/henrye/projects/clear_tasks/data/surface_forms_Thu02Apr_1025/train.tgt \
    -valid_src /home/henrye/projects/clear_tasks/data/surface_forms_Thu02Apr_1025/valid_single_ref.src \
    -valid_tgt /home/henrye/projects/clear_tasks/data/surface_forms_Thu02Apr_1025/valid_single_ref.tgt \
    -save_data /home/henrye/projects/clear_tasks/experiments/preprocess/surface_forms_02Apr_1042/sf \
    -dynamic_dict \
    -share_vocab
