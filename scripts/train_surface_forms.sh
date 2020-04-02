tensorboard_log_dir="/home/henrye/projects/clear_tasks/experiments/tensorboard"
train_dir_name="/home/henrye/projects/clear_tasks/experiments/train/surface_forms_02Apr_1117"
preprocess_dir_name="/home/henrye/projects/clear_tasks/experiments/preprocess/surface_forms_02Apr_1042"
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
    --report_every 500 \
    --valid_steps 500 \
    --save_checkpoint 1000 \
    --train_steps 25000 \
    --world_size 2 \
    --gpu_ranks 0 1 \
    --tensorboard \
    --tensorboard_log_dir "$tensorboard_log_dir"
