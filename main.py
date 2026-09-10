import subprocess
import sys

if __name__ == '__main__':
    subprocess.run([
        "powershell",
        "-Command",
        f'Start-Process "{sys.executable}" -ArgumentList "./src/dualsense_mouse.py" -Verb RunAs'
    ])
