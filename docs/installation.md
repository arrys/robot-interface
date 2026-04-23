# Installation

## Requirements
- Python 3.12+
- `uv` (recommended package manager for this repository)

## ur-rtde Build Prerequisites
`ur-rtde` may build from source on newer Python versions. Install these first:

- `cmake`
- `ninja` (sometimes written as "ginja", package name is `ninja`)
- Boost development package
- `git`

On Ubuntu/Debian:

```bash
sudo apt update
sudo apt install -y cmake ninja-build libboost-all-dev git
```

## Local Editable Install

```bash
uv sync --dev
```

## Run Tests

```bash
uv run pytest
```
