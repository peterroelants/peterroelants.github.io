# From A/B To RL Notebook Workflow

These notebooks are adapted candidates for a new "From A/B to RL" blog series.
They bridge fixed A/B experiments, online bandit learning, and delayed-feedback
policy learning.

## Candidate Posts

- `post_01_bayesian_ab_testing.ipynb`: From A/B to RL (1/3): Bayesian A/B Testing.
- `post_02_multi_armed_bandits.ipynb`: From A/B to RL (2/3): Multi-Armed Bandits.
- `post_03_delayed_feedback_menace.ipynb`: From A/B to RL (3/3): Continuous Learning to Delayed Rewards.

Other source-series posts were not copied because they were not part of the
requested three-post candidate set.

## Supporting Files

- `menace_engine.py`: Tic-tac-toe and MENACE training logic used by the third notebook.
- `menace_playable_app.py`: Inline Bokeh app used by the third notebook.

## Setup

Run commands from this directory:

```sh
uv sync
```

## Notes

- The notebooks are source copies, not generated Jekyll posts yet.
- Add a topic conversion script once publication dates, preview images,
  descriptions, tags, and target post paths are chosen.
- The existing published A/B-to-RL posts live separately under
  `notebooks/ab_to_rl/` and `_posts/blog/ab_to_rl/`.
