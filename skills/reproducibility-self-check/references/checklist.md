# Pre-submission reproducibility checklist

Source: https://repoready.ai/checklist

Self-check v0.1 · copied from the public checklist ("Copy as Markdown", English, 2026-11-06). Each item names the RepoReady requirement(s) behind it; the area guides (`guide-*.md`) explain each requirement.

## Environment

- [ ] Pin every dependency to an exact version
  Commit a lock file or exact version pins, and state the language version.
  RepoReady: Dependencies and versions are listed · The software environment is pinned
- [ ] Document hardware, operating system and run time
  Name the CPU or GPU, memory, operating system and run time of each experiment.
  RepoReady: Machine assumptions documented · Hardware, tools and versions

## Data

- [ ] Say exactly how to obtain every dataset
  Source, accession or URL, version, license and access steps, ideally as a download script.
  RepoReady: Input data can be obtained · Data sources have stable identifiers · Input retrieval is automated
- [ ] Explain restricted data and provide a stand-in
  Say why the data cannot be shared, how to request access, and add a synthetic sample.
  RepoReady: Input data can be obtained · Data sources have stable identifiers
- [ ] Include the preprocessing code, not only processed data
  Every step from raw data to analysis input is a script in the repository.
  RepoReady: Data preparation steps are documented

## Code and entry points

- [ ] Include the code for every reported result
  Numbers, figures and tables, including simulations and the baselines you compare against.
  RepoReady: Code for each result is available
- [ ] Use relative paths only
  Read file locations from a config file or a command-line argument.
  RepoReady: Machine assumptions documented
- [ ] Provide one documented entry point
  A Makefile, workflow or script that performs every step in order, with its command.
  RepoReady: Instructions explain how to run the analysis · One command produces the results

## Randomness and statistics

- [ ] Set, record and report random seeds
  Seed every random number generator, make seeds configurable, and state them in the paper.
  RepoReady: Random seeds and variability are controlled
- [ ] Report the number of runs and the variability
  Runs or seeds per result, with error bars or confidence intervals and how they were computed.
  RepoReady: Random seeds and variability are controlled

## Outputs and figures

- [ ] Map every figure and table to its script
  A README table with paper item, script, input and output.
  RepoReady: Code is linked to the paper’s results
- [ ] Write outputs to predictable, documented locations
  Save figures, tables, metrics and logs with the configuration and seed behind them.
  RepoReady: Instructions explain how to run the analysis

## Documentation

- [ ] Write a README from clone to results
  What the code does, how to install and run it, expected outputs, a repository map.
  RepoReady: Instructions explain how to run the analysis · Documented commands agree with the code
- [ ] Point from the code to the paper
  Comment method code with the section, equation, figure or table it implements.
  RepoReady: Code is linked to the paper’s results

## License, archive, citation

- [ ] Add an open-source license
  A LICENSE file in the repository root tells others how they may reuse the code.
  RepoReady: Journal policy
- [ ] Archive the paper version with a DOI
  Tag a release, archive it with a DOI, cite it, and add CITATION.cff.
  RepoReady: The exact code version is identified · Journal policy

## Manuscript alignment

- [ ] Write the code availability statement
  Repository URL, archive DOI, version, license and any access restrictions.
  RepoReady: Journal policy
- [ ] Check that the paper matches the code
  Methods, data splits, hyperparameters, seeds and reported numbers agree with code and outputs.
  RepoReady: Outputs correspond to the reported results
