# From A/B To RL Notebook Workflow

These notebooks are the source notebooks for the published three-part
"From A/B to RL" blog series.
They bridge fixed A/B experiments, online bandit learning, and delayed-feedback
policy learning.

## Posts

- `post_01_bayesian_ab_testing.ipynb`: From A/B to RL (1/3): Bayesian A/B Testing.
- `post_02_multi_armed_bandits.ipynb`: From A/B to RL (2/3): Bandits and Thompson Sampling.
- `post_03_delayed_feedback_menace.ipynb`: From A/B to RL (3/3): MENACE and Delayed Rewards.

This directory intentionally contains only the three notebooks used by the
series.

## Supporting Files

- `menace_engine.py`: Tic-tac-toe and MENACE training logic used by the third notebook.
- `menace_playable_app.py`: Inline Bokeh app used by the third notebook.
- `../../js/bokeh/3.9.1/`: the core and widget BokehJS bundles used by generated site pages.

## Setup

Run commands from this directory:

```sh
uv sync
```

To execute the notebooks headlessly while preserving Matplotlib figures in
their outputs, use the inline backend:

```sh
MPLBACKEND=module://matplotlib_inline.backend_inline .venv/bin/jupyter nbconvert \
  --to notebook --execute --inplace \
  --ExecutePreprocessor.timeout=600 \
  --ExecutePreprocessor.kernel_name=python3 post_*.ipynb
./from_ab_to_rl_convert.sh
```

After conversion, run `just clear-notebooks` from the repository root to remove
outputs and transient execution metadata before committing.

See the shared [figure accessibility guidance](../README.md#figure-accessibility)
for alt text on figures in generated posts.

Local notebook execution keeps the Bokeh app self-contained, so notebooks can
still be opened and rendered interactively without any site-specific setup.
When the Part 3 notebook is converted to a web page, the conversion command
replaces the inline Bokeh runtime with the version-pinned core and widget
bundles checked into `../../js/bokeh/3.9.1/`.

Cells tagged `lazy-bokeh` opt into the supported browser-side lazy loader. The
converter moves their standalone Bokeh embed
script into a hashed generated asset and loads it with an
`IntersectionObserver` when the output approaches the viewport. Optional
`lazy-bokeh-height=<pixels>` and `lazy-bokeh-title=<text>` tags provide the
placeholder height and accessible description. Untagged Bokeh outputs remain
inline.

## Notes

- The notebooks are the source for the generated Jekyll posts under
  `_posts/blog/from_ab_to_rl/`.
- The conversion script externalizes notebook-generated media and uses the
  version-pinned Bokeh bundles described above.

The MENACE support scripts are checked with Ruff and ty:

```sh
uv run ruff format --check menace_engine.py menace_playable_app.py
uv run ruff check menace_engine.py menace_playable_app.py
uv run ty check menace_engine.py menace_playable_app.py
```
