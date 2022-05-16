from typing import List
import os


def execute_cmd(cmd: str) -> List[str]:
    stream = os.popen(cmd)
    lines = stream.readlines()
    return [line.rstrip() for line in lines]

