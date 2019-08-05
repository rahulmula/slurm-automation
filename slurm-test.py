from prettytable import PrettyTable
import os, sys, re, itertools

gpu_logpath = "/home/taccuser/test-automation/out_gpu.log"

num_gpus = 0
with open(gpu_logpath, "r") as file:
    for line in file:
        num_gpus += 1
print("Number of GPUs:")
print(num_gpus)
