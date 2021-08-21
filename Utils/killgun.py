import os
from _common import SERVER_DIR
from signal import SIGINT, SIGTERM
from time import sleep

PID_FILE = os.path.join(SERVER_DIR, 'Gun', 'service', 'process.pid')


def is_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def kill() -> bool:

    def remove_pid_file(delay=0):
        sleep(delay)
        try:
            os.remove(PID_FILE)
        except OSError:
            return
        print(f"File '{PID_FILE}' was removed manually")

    def try_kill_unsafe(message: str) -> bool:
        print(message)
        print("Do you want to kill the process unsafe? (y/n)")
        if input().lower() not in ("y", "yes"):
            return False
        try:
            os.kill(pid, SIGTERM)
        except Exception as _e:
            print(f"Something went wrong! ({_e})")
            return False
        if is_running(pid):
            print(f"Something went wrong! (the process {pid} is still running)")
            return False
        remove_pid_file(3)
        print(f"The process {pid} was killed unsafe!")
        return True

    if not os.path.exists(PID_FILE):
        print(f"File '{PID_FILE}' does not exist! (most probably the process is not running)")
        return False

    with open(PID_FILE) as file:
        pid = file.readline().strip()

    if not pid or not pid.isdigit():
        print(f"Something went wrong (pid file '{PID_FILE}' is empty)")
        os.remove(PID_FILE)
        print("Empty pid file was removed")
        return False

    print(f"PID found: {pid}")
    print(f"Trying to kill the process...")

    pid = int(pid)
    try:
        os.kill(pid, 0)
    except OSError:
        print(f"Process {pid} does not exist!")
        remove_pid_file()
        return False

    try:
        os.kill(pid, SIGINT)
    except Exception as e:
        return try_kill_unsafe(f"Something went wrong! ({e})")

    if os.path.exists(PID_FILE):
        sleep(5)
        if is_running(pid):
            return try_kill_unsafe(f"Something went wrong! (the process {pid} is still running)")
        remove_pid_file(2)

    print(f"The process {pid} was successfully killed!")
    print()
    return True


if __name__ == '__main__':
    kill()
