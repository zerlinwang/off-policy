#!/bin/sh
env="StarCraft2"
map="3s_vs_3z"
algo="qmix"
exp="global_alllocal"
seed_max=1

echo "env is ${env}, map is ${map}, algo is ${algo}, exp is ${exp}, max seed is ${seed_max}"

for seed in $(seq ${seed_max}); do
    echo "seed is ${seed}:"
    CUDA_VISIBLE_DEVICES=2 python train/train_smac.py --env_name ${env}\
     --algorithm_name ${algo} --experiment_name ${exp} --map_name ${map}\
      --seed 3 --buffer_size 5000 --lr 5e-4 --batch_size 32 --use_soft_update\
       --hard_update_interval_episode 200 --num_env_steps 5000000 \
       --log_interval 3000 --eval_interval 20000 --user_name "zoeyuchao"\
       --use_global_all_local_state
    echo "training is done!"
done

