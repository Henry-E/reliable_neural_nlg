data_dir="/home/henrye/projects/clear_tasks/data/surface_forms_Fri15May_1102"
preprocess_dir="/home/henrye/projects/clear_tasks/experiments/preprocess/surface_forms_$(date '+%a%d%b_%H%M')"
mkdir -p "$preprocess_dir"

python ~/downloads/OpenNMT-py/preprocess.py \
    -train_src "$data_dir"/train.src \
    -train_tgt "$data_dir"/train.tgt \
    -valid_src "$data_dir"/valid_single_ref.src \
    -valid_tgt "$data_dir"/valid_single_ref.tgt \
    -save_data "$preprocess_dir"/sf \
    -dynamic_dict \
    -share_vocab
