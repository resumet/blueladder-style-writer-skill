# Blue Ladder skill installation and maintenance

## When the user asks to install this skill

This public repository is a distribution source. Installing a personal copy requires reading these files and writing to the recipient's supported skill destination. It does not require write access to `resumet/blueladder-style-writer-skill`.

Use the following source metadata:

| Field | Value |
| --- | --- |
| Repository | `resumet/blueladder-style-writer-skill` |
| HTTPS clone URL | `https://github.com/resumet/blueladder-style-writer-skill.git` |
| Ref | `main` |
| Skill path inside repository | `.` (repository root) |
| Skill name / destination folder | `blue-ladder-content-studio` |

1. Identify the installation mechanism supported by the user's current product and follow its own instructions and permissions. For a managed ChatGPT skill catalog, use that environment's skill installation workflow. Local filesystem installation does not register a skill in a separate ChatGPT account or workspace.
2. Read `SKILL.md` and keep its relative resource layout intact: `agents/`, `assets/`, `references/`, `scripts/`, and `requirements.txt`. The corpus contains 100 historical writing samples; they are style references, not current factual evidence.
3. For an available `install-skill-from-github.py` helper with these options, use `--repo resumet/blueladder-style-writer-skill --ref main --path . --name blue-ladder-content-studio`, plus the destination supported by that environment. A bare repository URL omits the required skill path, and deriving the name from `.` is invalid. Locate the actual helper rather than guessing an absolute system path.
4. For local Codex CLI or IDE setup, the manual HTTPS clone instructions in `README.md` use the user's local `.agents/skills/blue-ladder-content-studio` directory. They are not instructions to modify a managed ChatGPT installation. Preserve an existing installation and follow the user's update request; do not delete it automatically.
5. Verify the skill files at the real destination and, where supported, the catalog entry before reporting installation success. A downloaded repository, generated ZIP, or temporary extraction alone does not establish installation.

## Diagnose an installation failure

Identify the stage: source download, destination write, skill validation, or catalog registration. Report the actual error and the affected location, omitting credentials. Distinguish a public source read from an authenticated connector's allowed repositories and from the recipient's own installation permissions.

Do not infer permission denial solely from a guessed directory, a source repository being read-only, or the absence of a previously assumed installation path. Inspect the supported mechanism and its actual result. Respect any real policy or permission denial; do not change access controls to get around it.

If the environment does not support installing skills, state that limitation. A ZIP may still be offered as a download when useful, but do not describe it as a completed installation or imply that receiving it grants missing platform capabilities.

This repository is a standalone skill. It does not currently contain a `.codex-plugin/plugin.json` manifest, so a plugin-import workflow is a different operation.

## When maintaining this repository

Keep the skill's name and relative references consistent. When changing packaged skill files, run `python scripts/build_skill_zip.py` and then `python scripts/build_skill_zip.py --check` so the downloadable archive matches the source. README-only or installation-guidance changes do not change the runtime skill package.

See the official [Build skills](https://learn.chatgpt.com/docs/build-skills) and [Skill controls](https://learn.chatgpt.com/docs/enterprise/skills) documentation for product-specific discovery and administration boundaries.
