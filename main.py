
import multiprocessing
import os
import subprocess

def run_dobby():
    subprocess.run(["python", "dobby_bot.py"])

def run_funnel():
    subprocess.run(["python", "funnel_bot.py"])

if __name__ == "__main__":
    # Create processes for each bot
    p1 = multiprocessing.Process(target=run_dobby)
    p2 = multiprocessing.Process(target=run_funnel)

    # Start processes
    p1.start()
    p2.start()

    # Wait for processes to finish (they won't, unless they crash)
    p1.join()
    p2.join()
