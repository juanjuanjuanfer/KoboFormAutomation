import time

def cli_print(text: str, sleeptime: int =0.05, finaltime: int = 0.7, finalcharater: str = "") -> None:
    for i in text:
        print(i, end="", flush=True)
        time.sleep(sleeptime)
    print(finalcharater)
    time.sleep(finaltime)