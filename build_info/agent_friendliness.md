# Agent Friendliness

Responsibility: this note records the rationale and roadmap for making this
repository easier for coding agents to work in without overloading every session
with too much context. Keep active agent instructions in `AGENTS.md`; keep
project, architecture, and command references in `README.md`,
`build_info/site_overview.md`, and `build_info/jekyll.md`.

## Current Baseline

- `AGENTS.md` at the repository root is the primary always-on instruction file.
- Keep `AGENTS.md` concise and practical. It should point an agent to the
  correct source documents and capture active agent-specific behavior.
- Do not duplicate the full README, all internal docs, or long generated file
  lists inside `AGENTS.md`; point agents to the right files instead.

## Recommended Layers

1. Root `AGENTS.md`
   - Best default for Codex and the most portable agent-facing convention.
   - Should remain under a few pages and be updated when agents repeat mistakes.

2. Optional nested `AGENTS.md` files
   - Add only if a subtree has enough special rules to justify it.
   - Candidate areas: `notebooks/` for notebook conversion rules, or `_posts/`
     if publishing conventions become more detailed.

3. Optional repo skills in `.agents/skills`
   - Use only for repeatable workflows, not general rules.
   - Candidate future skills:
     - `notebook-post-conversion`: convert notebooks to Jekyll posts and verify
       generated HTML conventions.
     - `blog-post-review`: review content changes for links, metadata, MathJax,
       images, tags, and generated URL behavior.
     - `site-visual-check`: serve the site and inspect key pages after layout or
       CSS changes.

4. Optional vendor-specific files
   - Add `.github/copilot-instructions.md` only if GitHub Copilot non-agent
     features need repository-wide instructions beyond `AGENTS.md`.
   - Add `.cursor/rules` only if Cursor-specific scoped rules become useful.
   - Add `.codex/config.toml` only for project-scoped Codex configuration such
     as MCP servers or trusted workflow defaults.

## Research Summary

- OpenAI Codex documentation recommends durable repository guidance in
  `AGENTS.md`, covering layout, run/build/test commands, conventions, constraints,
  and what "done" means.
- Codex also supports `.agents/skills` for repeatable workflows. A skill should
  be focused on one job and include a `SKILL.md` with clear trigger conditions.
- The public AGENTS.md format is intentionally tool-neutral and used by multiple
  coding agents.
- Cursor, Claude Code, GitHub Copilot, Aider, and OpenCode all converge on the
  same pattern: keep project instructions focused, specific, scoped, and
  version-controlled.
- Vendor-specific rule systems are useful when a tool needs path-specific
  behavior, but they create duplication if added before there is a real workflow
  need.

## Sources

- OpenAI Codex best practices: https://developers.openai.com/codex/learn/best-practices
- OpenAI Codex AGENTS.md guide: https://developers.openai.com/codex/guides/agents-md
- OpenAI Codex skills guide: https://developers.openai.com/codex/skills
- AGENTS.md format: https://agents.md/
- Cursor rules: https://docs.cursor.com/context/rules
- Claude Code memory: https://docs.anthropic.com/en/docs/claude-code/memory
- GitHub Copilot repository instructions: https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions
- Aider conventions: https://aider.chat/docs/usage/conventions.html
- OpenCode rules: https://open-code.ai/en/docs/rules
