# A/B To RL Notebook Workflow

These notebooks support posts that connect A/B testing, Bayesian binary
feedback, bandits, and reinforcement learning ideas.

## Setup

Run commands from this directory:

```sh
uv sync
```

## Regenerate Posts

Execute the notebooks and convert them from this directory:

```sh
uv run jupyter nbconvert --execute --inplace beta-distribution-probabilities.ipynb beta-prior-sequential-binary-decisions.ipynb --ExecutePreprocessor.timeout=900 --NotebookClient.store_widget_state=False
./ab_to_rl_convert.sh
```

The conversion script writes generated HTML posts under
`_posts/blog/ab_to_rl/`.
After conversion, run `just clear-notebooks` from the repository root to remove
outputs and transient execution metadata before committing.

See the shared [figure accessibility guidance](../README.md#figure-accessibility)
for alt text on static figures in generated posts.

Both notebooks use Bokeh for interactive examples. Their conversion commands
replace the notebooks' CDN loader URLs with the version-matched site bundles
under `../../js/bokeh/3.9.1/` and lazy-load the tagged interactive outputs near
the viewport. Local notebook execution continues to use the notebooks' normal
CDN-based Bokeh setup.
