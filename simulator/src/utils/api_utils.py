import subprocess

def is_testbed():
    try:
        subprocess.run("pos_run", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except:
        return False