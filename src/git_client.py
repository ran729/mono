from typing import List, Optional

import bash_client


def get_diff_compared_to(branch: Optional[str]) -> List[str]:
    cmd = "git diff --name-only"

    if branch:
        cmd = f'{cmd} {branch}'

    return bash_client.execute_cmd(cmd)


def get_last_commit_hash() -> str:
    cmd = 'git rev-parse --short HEAD '
    return bash_client.execute_cmd(cmd)[0]
