# Diffusion Flow Matching Notebooks

This directory contains the source notebook and supporting files for the Flow
Matching blog post.

## Setup

To set up the environment for this notebook using the uv-managed project, sync
the environment from `pyproject.toml` and `uv.lock`:
```sh
uv sync
```

## Notebook

- `flow_matching_intro.ipynb`: A visual introduction to flow matching with a
  one-dimensional toy distribution.

## Regenerate the post

Run the following from this directory:

```sh
uv run jupyter nbconvert --to notebook --execute --inplace flow_matching_intro.ipynb --ExecutePreprocessor.timeout=600
./flow_matching_convert.sh
```

The conversion script writes the generated post under
`_posts/blog/diffusion_flow_matching/` and extracts notebook-generated static
figures under `images/notebook_outputs/diffusion_flow_matching/`. It also
externalizes media so the generated page can load figures as ordinary static
assets. After conversion, run `just clear-notebooks` from the repository root
to remove outputs and transient execution metadata before committing.

## Notes

- These notebooks are intended for research and educational purposes.
- For GPU acceleration, ensure you have a compatible CUDA setup.

See the shared [figure accessibility guidance](../README.md#figure-accessibility)
for alt text on static figures in generated posts.
