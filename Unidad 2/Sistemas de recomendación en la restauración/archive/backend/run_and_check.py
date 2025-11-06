import subprocess
import sys
import time
import urllib.request

PYTHON = r".\venv\Scripts\python.exe"
UVICORN_CMD = [PYTHON, "-m", "uvicorn", "backend.api:app", "--host", "127.0.0.1", "--port", "8000"]

def find_pid_on_port(port=8000):
    try:
        out = subprocess.check_output(["netstat", "-ano"], text=True)
    except Exception as e:
        print("netstat failed:", e)
        return None
    for line in out.splitlines():
        if f":{port} " in line or f":{port}\t" in line:
            parts = line.split()
            pid = parts[-1]
            return int(pid)
    return None

def kill_pid(pid):
    try:
        subprocess.check_call(["taskkill", "/PID", str(pid), "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Killed pid {pid}")
    except Exception as e:
        print(f"Failed to kill pid {pid}: {e}")


def fetch(url, timeout=10):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            data = r.read().decode('utf-8')
            print('FETCH OK:', url)
            print(data[:1000])
            return True
    except Exception as e:
        print('FETCH ERR:', e)
        return False


def main():
    # kill any process using port 8000
    pid = find_pid_on_port(8000)
    if pid:
        print('Found process on port 8000, killing', pid)
        kill_pid(pid)
        time.sleep(1)

    print('Starting uvicorn...')
    proc = subprocess.Popen(UVICORN_CMD, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        # give server a moment to start
        time.sleep(1.5)
        print('Requesting /')
        fetch('http://127.0.0.1:8000/')
        print('\nRequesting /clients')
        ok = fetch('http://127.0.0.1:8000/clients')
        print('\nReading server logs (stdout, stderr snippets):')
        try:
            out, err = proc.communicate(timeout=1)
        except Exception:
            # read available
            out = ''
            err = ''
            if proc.stdout:
                try:
                    out = proc.stdout.read()
                except Exception:
                    out = ''
            if proc.stderr:
                try:
                    err = proc.stderr.read()
                except Exception:
                    err = ''
        print('--- stdout ---')
        print(out[-2000:])
        print('--- stderr ---')
        print(err[-2000:])
    finally:
        print('Terminating uvicorn process...')
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()

if __name__ == '__main__':
    main()
