# DATA 607 automated R execution

The **R reproducibility** workflow checks submitted code on pull requests to
`main` and on pushes in repositories containing this workflow. Every push to an
open pull request reruns the applicable checks. Existing forks must sync this
workflow and enable Actions to get checks on fork-only pushes; otherwise opening
a pull request to the class repository is sufficient. GitHub may require a
maintainer to approve a fork's first workflow run.

## What runs

- New or modified `.R`, `.r`, `.Rmd`, and `.qmd` submissions are checked.
- Changes to data files or the validation tooling trigger a full audit.
- **Actions > R reproducibility > Run workflow** starts a full audit manually.
- README-only changes do not trigger the workflow.
- Each file runs in a fresh R session and a separate copy of the repository,
  from the folder containing that file. Nothing is committed back to the repo.
- An execution error, interactive file prompt, or 180-second timeout fails the
  check. All selected files are attempted even if an earlier file fails.
- Disabled chunks (`eval=FALSE`) produce warnings and are listed in the summary;
  a passing check covers enabled code only.

## Reading results

Open the pull request's **Checks** tab, or the repository's **Actions** tab.
The run summary lists each file's result. File annotations identify errors.
Download the **r-execution-results** artifact for individual logs, JSON results,
and R/package version information. Logs are retained for 14 days.

The workflow installs R 4.5.0 and the dependencies declared in this folder's
`DESCRIPTION`. Add any new required CRAN packages there when adopting a new
dependency. Package versions are recorded in execution logs; they are not locked.

The checks validate execution, not the correctness of the analysis or the final
Quarto HTML/PDF layout. No branch rules are changed and no automatic merges are
performed. Existing submissions, data, and the class README remain unchanged.
