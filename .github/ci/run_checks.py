"""Run files in isolated copies and publish useful GitHub check results."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


def escape(value):
    return str(value).replace('%', '%25').replace('\r', '%0D').replace('\n', '%0A')


def annotation(level, file, message):
    prop = escape(file).replace(',', '%2C').replace(':', '%3A')
    print(f'::{level} file={prop}::{escape(message)}', flush=True)


def main():
    source = Path.cwd()
    work = Path(os.environ['RUNNER_TEMP']) / 'r-reproducibility'
    results_dir = work / 'results'
    results_dir.mkdir(parents=True, exist_ok=True)
    files = json.loads((work / 'files.json').read_text())
    results = []
    for index, file in enumerate(files):
        run_dir = work / 'workspaces' / str(index)
        shutil.copytree(source, run_dir, ignore=shutil.ignore_patterns('.git'), dirs_exist_ok=True)
        result_file = results_dir / f'{index:03d}.json'
        log_file = results_dir / f'{index:03d}.log'
        print(f'Running: {file}', flush=True)
        try:
            with log_file.open('w') as log:
                process = subprocess.run(
                    ['Rscript', '--vanilla', str(source / '.github/ci/execute.R'),
                     Path(file).name, str(result_file)], cwd=run_dir / Path(file).parent,
                    stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                    timeout=180,
                )
            if result_file.exists():
                result = json.loads(result_file.read_text(errors='replace'))
            else:
                result = {'status': 'FAIL', 'error': f'R exited with code {process.returncode}; see {log_file.name}.'}
            if process.returncode != 0:
                result['status'] = 'FAIL'
        except subprocess.TimeoutExpired:
            result = {'status': 'FAIL', 'error': 'Execution exceeded the 180-second limit; check for interactive input or unavailable data.'}
        result['file'] = file
        results.append(result)
        result_file.write_text(json.dumps(result, indent=2))
        if result['status'] == 'FAIL':
            annotation('error', file, result.get('error', 'Execution failed.'))
            print(log_file.read_text(errors='replace')[-10000:])
        skipped = result.get('skipped_chunks', [])
        if skipped:
            if isinstance(skipped, str):
                skipped = [skipped]
            annotation('warning', file, f'{len(skipped)} disabled chunk(s) were not executed: {", ".join(skipped)}. Passing only covers enabled code.')
        shutil.rmtree(run_dir)
    (results_dir / 'results.json').write_text(json.dumps(results, indent=2))
    with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as summary:
        summary.write('\n### R execution results\n\n| File | Result | Disabled chunks |\n| --- | --- | --- |\n')
        for result in results:
            skipped = result.get('skipped_chunks', [])
            count = 1 if isinstance(skipped, str) else len(skipped)
            filename = result['file'].replace('|', '&#124;').replace('`', '')
            summary.write(f'| `{filename}` | {result["status"]} | {count} |\n')
        summary.write('\nDownload **r-execution-results** for per-file logs and errors. '
                      'Each file runs in a fresh R session from its own folder with the repository files available. '
                      'Disabled chunks are reported but not executed. '
                      'This tests R execution, not final HTML/PDF rendering or analytical correctness.\n')
    return int(any(r['status'] == 'FAIL' for r in results))


if __name__ == '__main__':
    sys.exit(main())
