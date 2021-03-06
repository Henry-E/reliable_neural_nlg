tensorboard_log_dir="/home/henrye/projects/clear_tasks/experiments/tensorboard"
preprocess_dir_name="/home/henrye/projects/clear_tasks/experiments/preprocess/surface_forms_Tue12May_1103"
train_dir_name="/home/henrye/projects/clear_tasks/experiments/train/surface_forms_$(date '+%a%d%b_%H%M')"
mkdir -p "$train_dir_name"
python /home/henrye/downloads/OpenNMT-py/train.py \
    -data "$preprocess_dir_name"/sf \
    -save_model "$train_dir_name"/sf \
    -log_file "$train_dir_name"/sf.log.txt \
    --optim adam \
    --learning_rate 0.001 \
    --encoder_type brnn \
    --layers 2 \
    --batch_size 64 \
    --word_vec_size 300 \
    --rnn_size 600 \
    --share_embeddings \
    --copy_attn \
    --copy_attn_force \
    --report_every 300 \
    --valid_steps 300 \
    --save_checkpoint 300 \
    --train_steps 6600 \
    --world_size 2 \
    --gpu_ranks 0 1 \
    --tensorboard \
    --tensorboard_log_dir "$tensorboard_log_dir"
