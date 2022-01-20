import signal
import os

if __name__ == "__main__":
    
    with open("pids.txt", "r") as f:
        pids = f.read()
        listpids = list(pids.strip('][').split(', '))

        for p in listpids:
            os.kill(int(p), signal.SIGTERM)
