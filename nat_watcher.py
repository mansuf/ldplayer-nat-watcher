import sys
import logging
from wmi import WMI

ldplayer_nat_proc_name = "VBoxNetNAT.exe"

def setup_logging(name_module, verbose=False):
    log = logging.getLogger(name_module)
    handler = logging.StreamHandler()
    fmt = logging.Formatter("[%(levelname)s] %(message)s")
    handler.setFormatter(fmt)
    log.addHandler(handler)
    if verbose:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)
    return log

log = setup_logging("nat_watcher")
wmi = WMI()

def get_ldplayer_nat_process():
    log.info("Searching for LDPlayer NAT Process...")

    nat_proc = None
    for proc in wmi.Win32_Process():
        if proc.Name == ldplayer_nat_proc_name:
            nat_proc = proc
            break

    if nat_proc is None:
        log.error("LDPlayer NAT Process cannot be found")
        return None

    log.info(f"LDPlayer NAT Process is found, PID: {nat_proc.ProcessId}")
    log.info(f"App arguments = {nat_proc.CommandLine}")
    return nat_proc

def create_ldplayer_nat_process(proc):
    pid, _ = wmi.Win32_Process.Create(proc.CommandLine, None, None)
    log.info(f"LDPlayer NAT Process has been created, PID = {pid}")

nat_proc = get_ldplayer_nat_process()
if nat_proc is None:
    sys.exit(1)

log.info("Watching LDPlayer NAT Process...")

proc_watcher = wmi.Win32_Process.watch_for("deletion")
while True:
    proc = proc_watcher()
    if proc.Name == ldplayer_nat_proc_name:
        log.info("LDPlayer NAT Process is nuked for unknown reasons, recreating...")
        create_ldplayer_nat_process(proc)
