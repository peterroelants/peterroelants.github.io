# Project command runner for Peter's Notes.

set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

detected_bundle := `if [ -x /opt/homebrew/opt/ruby@3.3/bin/bundle ]; then echo /opt/homebrew/opt/ruby@3.3/bin/bundle; else command -v bundle || echo bundle; fi`
detected_ruby := `if [ -x /opt/homebrew/opt/ruby@3.3/bin/ruby ]; then echo /opt/homebrew/opt/ruby@3.3/bin/ruby; else command -v ruby || echo ruby; fi`

bundle := env_var_or_default("BUNDLE", detected_bundle)
npm := env_var_or_default("NPM", "npm")
ruby := env_var_or_default("RUBY", detected_ruby)
uv := env_var_or_default("UV", "uv")

export BUNDLE_USER_HOME := env_var_or_default("BUNDLE_USER_HOME", ".bundle")
export RUBYOPT := env_var_or_default("RUBYOPT", "-EUTF-8")
export UV_CACHE_DIR := env_var_or_default("UV_CACHE_DIR", ".uv-cache")

# List available commands.
default:
    @just --list

# Show local tool versions.
tools:
    {{ruby}} -v
    {{bundle}} -v
    node -v
    {{npm}} -v
    {{uv}} --version
    just --version

# Install Ruby and Node dependencies from the checked-in locks.
setup:
    {{bundle}} install
    {{npm}} ci

# Run fast, non-destructive checks.
check: check-convert-scripts
    git diff --check
    {{bundle}} check
    {{npm}} ls --depth=0
    {{uv}} run notebooks/notebook_convert.py --help >/dev/null

# Check notebook conversion shell scripts for syntax errors.
check-convert-scripts:
    bash -n \
      notebooks/ab_to_rl/ab_to_rl_convert.sh \
      notebooks/agents/openai/agents_openai_convert.sh \
      notebooks/cross_entropy/cross_entropy_convert.sh \
      notebooks/diffusion_flow_matching/flow_matching_convert.sh \
      notebooks/from_ab_to_rl/from_ab_to_rl_convert.sh \
      notebooks/gaussian_process/gaussian_process_convert.sh \
      notebooks/misc/misc_convert.sh \
      notebooks/neural_net_implementation/neural_net_implementation_convert.sh \
      notebooks/rnn_implementation/rnn_implementation_convert.sh

# Clear all outputs from notebooks in place.
clear-notebooks:
    find notebooks -name '*.ipynb' -print0 | xargs -0 {{uv}} run --with nbconvert jupyter nbconvert --clear-output --inplace

# Build minified CSS assets.
css-build:
    {{npm}} run css:build

# Watch and rebuild minified CSS assets.
css-watch:
    {{npm}} run css:watch

# Build the static site.
build: css-build
    {{bundle}} exec jekyll build --trace

# Serve the site locally.
serve: css-build
    {{bundle}} exec jekyll serve

# Run Jekyll's site diagnostics.
doctor:
    {{bundle}} exec jekyll doctor

# Run the standard local verification pass.
verify: check build doctor

# Update the GitHub Pages gem bundle.
update-github-pages:
    {{bundle}} update github-pages

# Update all Ruby gems in Gemfile.lock.
update-gems:
    {{bundle}} update --all
