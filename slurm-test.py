from prettytable import PrettyTable
import os, sys, re, itertools, subprocess, json
from subprocess import PIPE, run


gpu_logpath = "/home/taccuser/slurm-automation/out_gpu.log"
conf_path="/home/taccuser/slurm-automation/conf.json"
srun_command = "srun -N 1 --gres=gpu:2 hostname"
autodetect_singlenode_command = "salloc -N 1 --gres=gpu:2 --begin=now --time=10"
autodetect_multinode_command = "salloc -N 2 --gres=gpu:2 --begin=now --time=10"
sinfo_command = "sinfo -Nl"
regex=r'^node-name:.*$'
nodepath = "/home/taccuser/slurm-automation/totalnodes.log"
alloc_regex=r'^salloc:.*$'
cancel_regex=r'.*?Granted.*$'


num_gpus = 0
with open(gpu_logpath, "r") as file:
    for line in file:
        num_gpus += 1
print("Number of GPUs:")
print(num_gpus)


x = PrettyTable()
x.field_names = ["Slurm Test Scenarious","Result"]

def cmdline(command):
    process = Popen(args=command, stdout=PIPE, shell=True)
    return process.communicate()[0]

def slurm_group_gpudetection():          
    with open(nodepath, "r") as file:
        for line in file:
            if "debug*" in line:
               print('Found keyword')
               print(line)
               str = line.split(" ")
               print(str[0])
        

def slurm_gpudetect():
    res = os.popen("%s" %srun_command).read()
    res_out = res.strip() #strip: removes spaces from output
    file1 = open("test-server.log","r")
    var = re.findall(r'node-name:(.*?)(?=\s*,\s*node-name:|$)', file1.read())    
    str1 = ''.join(var)
    if res_out == str1:       
        x.add_row(["Total No.of Gpu vs Slurm No.of Gpu detecting", "Pass"])
    else:
        x.add_row(["Total No.of Gpu vs Slurm No.of Gpu detecting", "Fail"])
        
def cancel_allocation():
    with open("/home/taccuser/slurm-automation/allocation.log", "r") as file:
        for line in file:
            for match in re.finditer(cancel_regex, line, re.S):
                str = match.group().split(" ")
                str.reverse()
                print(str[0])
                os.popen("scancel %s" %str[0])


def validate_output():
    print("you have not entered")
    try:
        with open("/home/taccuser/slurm-automation/allocation.log", "r") as file:
            if "error" in file.read():           
                x.add_row(["GPU autodetect single-node allocation", "Fail"])            
            else:
                x.add_row(["GPU autodetect single-node allocation", "Pass"])
                str = os.popen("sinfo").read()
                print(str)
    except:
        pass
                
def slurm_node_allocation(autodetect_command):
    try:        
        res = subprocess.run("%s 2>&1 | tee allocation.log >/dev/tty" %autodetect_command, timeout=2, shell=True)        
        print(res)
        validate_output()
    except:
        pass        
        print("Pass")
        validate_output()


def slurm_load_conf(var):
    config = json.loads(open(conf_path).read())
    return config["%s" %var]

def slurm_automatic_allocation(n1hostname,n1autoallocation_command):
    n1host = slurm_load_conf(n1hostname)
    n1_autoallocation = slurm_load_conf(n1autoallocation_command)
    #allocate  =  os.popen("%s" %n1_autoallocation).read()   
    allocate = subprocess.run("%s" %n1_autoallocation, stdout=subprocess.PIPE, timeout=5, shell=True)    
    var = allocate.stdout.decode()
    res = var.strip()
    if n1host == res:
        print("Pass")
        x.add_row(["Auto node allocation", "Pass"])       
    else:
        print("Fail")
        x.add_row(["Auto node allocation", "Fail"])        

def slurm_autonode_allocation():
    try:
        slurm_automatic_allocation("N1hostname","N1_autoallocation")
        nodeexist = slurm_load_conf("N2hostname")
        print(nodeexist)
        print("N2 has error")
        if nodeexist != "None":
            print("Multi-Node exist!")
            slurm_automatic_allocation("N2hostname","N2_autoallocation")        
        else:
            print("Multi-Node not exist!")
    except:
        pass

slurm_gpudetect()
slurm_node_allocation(autodetect_singlenode_command)
cancel_allocation()

#slurm_node_allocation(autodetect_multinode_command)
#slurm_gpu_autodetect() 
#slurm_load_conf()

slurm_autonode_allocation()
print(x)
#slurm_group_gpudetection()
