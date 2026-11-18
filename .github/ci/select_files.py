"""Select changed submissions, or audit all after data/tooling changes."""
import json
import os
from pathlib import Path
import subprocess

SOURCE = {'.r', '.rmd', '.qmd'}
DATA = {'.csv', '.xlsx', '.xls', '.rds', '.rdata', '.json', '.txt'}


def git(*args):
    return subprocess.check_output(['git', *args]).decode().strip()


def select(tracked, changed=None):
    submissions = sorted(p for p in tracked if Path(p).suffix.lower() in SOURCE
                         and not p.startswith('.github/'))
    if changed is None or any(
        p.startswith('.github/ci/') or p == '.github/workflows/r-reproducibility.yml'
        or Path(p).suffix.lower() in DATA for p in changed
    ):
        return submissions
    return [p for p in submissions if p in changed]


def main():
    event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text())
    kind = os.environ['GITHUB_EVENT_NAME']
    tracked = git('ls-files', '-z').rstrip('\0').split('\0')
    changed = None
    if kind == 'pull_request':
        base = event['pull_request']['base']['sha']
        head = event['pull_request']['head']['sha']
        comparison = [f'{base}...{head}']
    elif kind == 'push' and event.get('before', '').strip('0'):
        comparison = [event['before'], os.environ['GITHUB_SHA']]
    else:
        comparison = None
    if comparison:
        changed = set(git('diff', '--name-only', '-z', *comparison).rstrip('\0').split('\0'))
    files = select(tracked, changed)
    work = Path(os.environ['RUNNER_TEMP']) / 'r-reproducibility'
    work.mkdir(parents=True, exist_ok=True)
    (work / 'files.json').write_text(json.dumps(files))
    with open(os.environ['GITHUB_OUTPUT'], 'a') as output:
        output.write(f'count={len(files)}\n')
    with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as summary:
        summary.write(f'### Selected submissions\n\n{len(files)} R source files selected.\n\n')
        summary.write('\n'.join(f'- `{p}`' for p in files) + '\n')
    print(json.dumps(files, indent=2))


if __name__ == '__main__':
    main()
