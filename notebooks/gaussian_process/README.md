# Gaussian Process Notebooks

Responsibility: this document describes the runtime environment for executing
the Gaussian process notebooks. Keep notebook conversion details in
`../README.md`; this file is only for this topic's dependencies and local
notebook commands.

## Environment

Use the uv-managed project in this directory:

```sh
cd notebooks/gaussian_process
uv sync
```

The environment is intentionally a modern runnable setup for the notebooks, not
a byte-for-byte recreation of the historical Conda environments used when the
posts were first written. `pyproject.toml` declares the dependency policy and
`uv.lock` pins the resolved package set. The current environment uses Python
3.13 with modern JAX, Optax, Bokeh, NumPy, Pandas, and SciPy releases.

## Running

Start Jupyter from this directory so relative data paths resolve:

```sh
uv run jupyter lab
```

For a quick import check:

```sh
uv run python -c "import jax, optax, numpy, pandas, scipy, bokeh"
```

## VS Code

The repository includes VS Code settings that point the Python/Jupyter
extensions at this directory's uv environment:

```text
notebooks/gaussian_process/.venv/bin/python
```

Run `uv sync` before opening or selecting a kernel. In a notebook, choose the
Python environment above from the kernel picker. The workspace setting
`jupyter.notebookFileRoot` runs notebooks from their own directory so local data
files such as `monthly_in_situ_co2_mlo.csv` resolve correctly.

## Converting Posts

Notebook execution and notebook conversion are separate steps. After editing and
executing notebooks, convert the generated posts with:

```sh
./gaussian_process_convert.sh
```
