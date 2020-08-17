#!/sbin/python3
import os
import sys
import psutil
import json
import serial
import time

__config = None

def load_config():
    global __config
    config_file = "config.json"
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            __config = json.load(f)
    else:
        print("Unable to find config file: %s" % config_file)

def save_config():
    config_file = "config.json"
    with open(config_file, "w+") as f:
        f.write(json.dumps(__config))
        f.flush()
        f.close()

def get_processes_list():
    return psutil.process_iter(['pid', 'name', 'username'])

def print_help():
    print("proc_monitor list")
    print("proc_monitor action <port> <baud>")
    print("proc_monitor watch <name> <pid>")

if __name__ == "__main__":
    load_config()
    if len(sys.argv) < 2:
        print_help()
        sys.exit(-1)
    cmd = sys.argv[1]
    print(cmd)
    if cmd == "list":
        for proc in get_processes_list():
            print(proc.info)
    if cmd == "action":
        if len(sys.argv) != 4:
            print_help()
            sys.exit(-1)
        __config["action"]["port"] = sys.argv[2]
        __config["action"]["baud"] = int(sys.argv[3])
        save_config()
    if cmd == "watch":
        if len(sys.argv) != 4:
            print_help()
            sys.exit(-1)
        proc_name = sys.argv[2]
        proc_pid = int(sys.argv[3])
        with serial.Serial(__config["action"]["port"], __config["action"]["baud"]) as ser:
            ser.write("led off\n".encode("utf-8"))
            ser.flush()
            while True:
                proc_list = get_processes_list()
                found = False
                for proc in proc_list:
                    if proc_name == proc.name() and proc_pid == proc.pid:
                        found = True
                        break
                if found:
                    print("Process is running")
                    ser.write("led on\n".encode("utf-8"))
                    ser.flush()
                else:
                    print("Process was stopped")
                    ser.write("led blink\n".encode("utf-8"))
                    ser.flush()
                    break
                time.sleep(1)