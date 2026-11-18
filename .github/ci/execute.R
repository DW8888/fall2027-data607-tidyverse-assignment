# Called once per submission by run_checks.py; no student files are edited.
args <- commandArgs(trailingOnly = TRUE)
file <- args[[1]]
result_path <- args[[2]]
options(timeout = 60, repos = c(CRAN = 'https://cloud.r-project.org'))
execution_env <- new.env(parent = globalenv())
skipped <- character()
errors <- character()
status <- 'PASS'
detail <- ''

interactive_call <- function(x) {
  if (!is.recursive(x)) return(FALSE)
  if (is.call(x)) {
    name <- paste(deparse(x[[1]]), collapse = '')
    if (name %in% c('file.choose', 'base::file.choose', 'readline',
                    'base::readline', 'menu', 'utils::menu',
                    'select.list', 'utils::select.list')) return(TRUE)
  }
  any(vapply(as.list(x), interactive_call, logical(1)))
}

check_interactive <- function(code) {
  parsed <- tryCatch(parse(text = code), error = function(e) NULL)
  if (!is.null(parsed) && interactive_call(parsed)) {
    stop('Interactive input (such as file.choose()) is not reproducible. Use an included file or accessible URL.', call. = FALSE)
  }
}

tryCatch({
  if (tolower(tools::file_ext(file)) == 'r') {
    check_interactive(readLines(file, warn = FALSE))
    sys.source(file, envir = execution_env)
  } else {
    knitr::opts_chunk$set(error = FALSE, dev = 'png', fig.path = 'ci-figures/')
    knitr::opts_knit$set(rmarkdown.pandoc.to = 'html', rmarkdown.runtime = 'static')
    knitr::opts_hooks$set(eval = function(options) {
      if (isFALSE(options$eval)) {
        skipped <<- c(skipped, options$label)
      } else {
        check_interactive(options$code)
      }
      options
    })
    # Also fail if a student explicitly uses error=TRUE to keep rendering.
    knitr::knit_hooks$set(error = function(x, options) {
      errors <<- c(errors, x)
      x
    })
    knitr::knit(file, output = 'ci-execution.md', envir = execution_env, quiet = FALSE)
    if (length(errors)) stop(paste(errors, collapse = '\n'), call. = FALSE)
  }
}, error = function(e) {
  status <<- 'FAIL'
  detail <<- conditionMessage(e)
})

jsonlite::write_json(list(file = file, status = status, error = detail,
    skipped_chunks = unname(skipped), R_version = R.version.string),
    result_path, pretty = TRUE, auto_unbox = TRUE)
print(sessionInfo())
if (status == 'FAIL') message(detail)
quit(status = if (status == 'FAIL') 1 else 0)
