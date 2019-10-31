import os, sys, re, itertools, subprocess, json
from subprocess import PIPE, run
from prettytable import PrettyTable

gpu_logpath = "/home/taccuser/slurm-automation/out_gpu.log"
conf_path="/home/taccuser/slurm-automation/conf.json"
srun_command = "srun -N 1 --gres=gpu:2 hostname"
autodetect_singlenode_command = "salloc -N 1 --gres=gpu:2 --begin=now --time=10"
autodetect_multinode_command = "salloc -N 2 --gres=gpu:2 --begin=now --time=10"
sinfo_command = "sinfo -Nl"
regex=r'^node-name:.*$'
nodepath = "/home/taccuser/slurm-automation/totalnodes.log"
node_allocation_regex=r'^salloc:.*$'
node_cancel_regex=r'.*?Granted.*$'
x = PrettyTable()
x.field_names = ["Slurm Test Scenarious","Result"]



def slurm_load_conf(var):
    config = json.loads(open(conf_path).read())
    return config["%s" %var]


#def total_gpu():
#    num_gpus = 0
#    with open(gpu_logpath, "r") as file:
#        for line in file:
#            num_gpus += 1
#    print("Number of GPUs:")
#    print(num_gpus)

#def slurm_verify_rocmcomponent():


#def cmdline(command):
#    process = Popen(args=command, stdout=PIPE, shell=True)
#    return process.communicate()[0]

def slurm_group_gpudetection():          
    with open(nodepath, "r") as file:
        for line in file:
            if "debug*" in line:                   
               print(line)
               str = line.split(" ")
               print(str[0])
        

def slurm_master_setup():
    res = os.popen("sinfo").read()    
    if "NODELIST" in res:        
        x.add_row(["Slurm Master Setup", "Pass"])
    else:
        x.add_row(["Slurm Master Setup", "Fail"])


def slurm_node_setup():
    res = os.popen("sinfo").read()
    nodename = slurm_load_conf("N1hostname")
    if nodename in res:        
        x.add_row(["Slurm Node Setup", "Pass"])
    else:    
        x.add_row(["Slurm Node Setup", "Fail"])
  


#def slurm_gpudetect():
#    res = os.popen("%s" %srun_command).read()
#    res_out = res.strip() #strip: removes spaces from output
#    print(res_out)
#    file1 = open("test-server.log","r")
#    var = re.findall(r'node-name:(.*?)(?=\s*,\s*node-name:|$)', file1.read()) #identifying the nodename    
#    str1 = ''.join(var)
#    print(str1)
#    if res_out == str1:       
#        x.add_row(["Total No.of Gpu vs Slurm No.of Gpu detecting", "Pass"])
#    else:
#        x.add_row(["Total No.of Gpu vs Slurm No.of Gpu detecting", "Fail"])


def slurm_gpu_detect():
    nodename = slurm_load_conf("N1hostname")
    res=os.popen("srun -w %s /opt/rocm/bin/rocm_agent_enumerator" %nodename).read()
    slurm_gpu_detected =  int(res.count("gfx") -1)
    node_gpu_devices = int(slurm_load_conf("N1cards"))
    
    if (node_gpu_devices == slurm_gpu_detected):
        x.add_row(["Total No.of Gpu vs Slurm No.of Gpu detecting", "Pass"])
    else:
        x.add_row(["Total No.of Gpu vs Slurm No.of Gpu detecting", "Fail"])



def cancel_allocation():
    with open("/home/taccuser/slurm-automation/allocation.log", "r") as file:
        for line in file:
            for match in re.finditer(node_cancel_regex, line, re.S):
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
            
    except:
        pass
                
def slurm_node_allocation(autodetect_command):
    try:        
        res = subprocess.run("%s 2>&1 | tee allocation.log >/dev/tty" %autodetect_command, timeout=2, shell=True)        
        validate_output()
    except:
        pass       
        
        validate_output()



def slurm_auto_allocation(n1hostname,n1autoallocation_command):
    n1host = slurm_load_conf(n1hostname)
    n1_autoallocation = slurm_load_conf(n1autoallocation_command)
    #allocate  =  os.popen("%s" %n1_autoallocation).read()   
    allocate = subprocess.run("%s" %n1_autoallocation, stdout=subprocess.PIPE, timeout=5, shell=True)    
    var = allocate.stdout.decode()
    res = var.strip()
    if n1host == res:    
        x.add_row(["Node allocation with --gpu", "Pass"])       
    else:        
        x.add_row(["Node allocation with --gpu", "Fail"])        

def slurm_autonode_allocation():
    try:
        slurm_auto_allocation("N1hostname","N1_autoallocation")
        nodeexist = slurm_load_conf("N2hostname")        
        print("N2 has error")
        if nodeexist != "None":
            print("Multi-Node exist!")
            slurm_auto_allocation("N2hostname","N2_autoallocation")        
        else:
            print("Multi-Node not exist!")
    except:
        pass

def slurm_gpu_separation():
    try:
        nodename = slurm_load_conf("N1hostname")
        res=os.popen("srun -w %s --gres=gpu:1 /opt/rocm/bin/rocm_agent_enumerator" %nodename).read()
        slurm_gpu_detected =  int(res.count("gfx") -1)
        if slurm_gpu_detected == 1:            
            x.add_row(["Gpu segregation", "Pass"])
        else:            
            x.add_row(["Gpu segregation", "Fail"])

    except:
        pass




slurm_master_setup()
slurm_node_setup()


slurm_gpu_detect()

#slurm_gpudetect()
slurm_node_allocation(autodetect_singlenode_command)
cancel_allocation()
slurm_autonode_allocation()
slurm_gpu_separation()
print(x)


#slurm_group_gpudetection()
