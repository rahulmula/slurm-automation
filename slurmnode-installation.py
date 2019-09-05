import os, sys, re, itertools, subprocess, json
from subprocess import PIPE, run, call
from prettytable import PrettyTable

ansible_path="/home/taccuser/slurm_ansible_scripts/"

def slurm_node_install():
    os.system("cd %s && ansible-playbook install_slurm-node.yml" %ansible_path)


slurm_node_install()

