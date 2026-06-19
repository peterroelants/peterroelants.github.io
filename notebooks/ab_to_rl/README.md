# A/B To RL Notebook Workflow

These notebooks support posts that connect A/B testing, Bayesian binary
feedback, bandits, and reinforcement learning ideas.

## Setup

Run commands from this directory:

```sh
uv sync
```

## Regenerate Posts

Execute the notebooks, convert them, then clear outputs before committing:

```sh
uv run jupyter nbconvert --execute --inplace beta-distribution-probabilities.ipynb beta-prior-sequential-binary-decisions.ipynb --ExecutePreprocessor.timeout=900 --NotebookClient.store_widget_state=False
./ab_to_rl_convert.sh
./.venv/bin/jupyter nbconvert --clear-output --ClearOutputPreprocessor.remove_metadata_fields=execution --ClearMetadataPreprocessor.enabled=True --ClearMetadataPreprocessor.clear_cell_metadata=False --ClearMetadataPreprocessor.clear_notebook_metadata=True --ClearMetadataPreprocessor.preserve_nb_metadata_mask=kernelspec --ClearMetadataPreprocessor.preserve_nb_metadata_mask=language_info --inplace beta-distribution-probabilities.ipynb beta-prior-sequential-binary-decisions.ipynb
```

The conversion script writes generated HTML posts under
`_posts/blog/ab_to_rl/`.
