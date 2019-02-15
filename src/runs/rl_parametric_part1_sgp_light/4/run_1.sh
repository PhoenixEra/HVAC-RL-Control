python ../../../a3c_eplus_rlParametric_v0.1.py --env Part1-Light-Sgp-Train-v1 --max_interactions 2500000 --window_len 16 \
--state_dim 71 --num_threads 16 --action_space part1_v1 --save_freq 500000 --eval_freq 100000 \
--job_mode Train --test_env Part1-Light-Sgp-Test-v1 Part1-Light-Sgp-Test-v2 Part1-Light-Sgp-Test-v3 Part1-Light-Sgp-Test-v4 \
--train_act_func part1_v1 --eval_act_func part1_v1 \
--reward_func part1_v1 --metric_func part1_v1 --init_e 0.0 --rwd_e_para 1.2 --rwd_p_para 1.0 \
--h_regu_frac 0.0 --forecast_dim 0 --rmsprop_decay 0.99 --rmsprop_momet 0.0 --train_freq 5 \
--violation_penalty_scl 10 --eval_epi_num 1 --activation linear --model_type nn --model_param 73 1 \
--learning_rate 0.00005 --learning_rate_decay_rate 1.0 --learning_rate_decay_steps 100000 --debug_log_prob 0.0005 \
--isNoisyNet True --isNoisyNetEval_rmNoise True \
--is_warm_start True --model_dir Part1-Light-Sgp-Train-v1-res1/model_data/model.ckpt-2500000
