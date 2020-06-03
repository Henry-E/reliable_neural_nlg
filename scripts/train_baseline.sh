tensorboard_log_dir="/home/henrye/projects/clear_tasks/experiments/tensorboard"
preprocess_dir_name="/home/henrye/projects/clear_tasks/experiments/preprocess/baseline_Mon18May_0936"
train_dir_name="/home/henrye/projects/clear_tasks/experiments/train/baseline_$(date '+%a%d%b_%H%M')"
mkdir -p "$train_dir_name"
python /home/henrye/downloads/OpenNMT-py/train.py \
    -data "$preprocess_dir_name"/baseline \
    -save_model "$train_dir_name"/baseline \
    -log_file "$train_dir_name"/baseline.log.txt \
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
    --tensorboard_log_dir "$tensorboard_log_dir"/baseline
