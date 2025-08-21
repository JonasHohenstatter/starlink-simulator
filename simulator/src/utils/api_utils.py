import subprocess

def is_testbed():
    try:
        subprocess.run("pos_run", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return False
    except:
        return True