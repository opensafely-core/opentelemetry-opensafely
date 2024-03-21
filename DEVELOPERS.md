# Notes for developers

## System requirements

### just

```sh
# macOS
brew install just

# Linux
# Install from https://github.com/casey/just/releases

# Add completion for your shell. E.g. for bash:
source <(just --completions bash)

# Show all available commands
just #  shortcut for just --list
```


## Local development environment

Set up a local development environment with:
```
just devenv
```

## Tests
Run the tests with:
```
just test <args>
```

## Building the package

Test that the package builds

```
just package-test whl
just package-test sdist
```

## Create a new release from current main

This pulls `main`, checks out a new release branch, creates and commits a new
`version` file, and opens a PR. Github actions will deal with tagging the new version.

```
just release
```
