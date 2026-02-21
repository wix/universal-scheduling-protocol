# AGENTS.md

## Change Log Policy

After completing any set of file changes in this repository, you MUST append a new entry to the root-level `CHANGE_LOG.md` file before finishing your response.

### Entry format

Each entry is a level-2 heading followed by a bulleted list:

    ## DD/MM/YY at HH:MM:SS by <git_username>

    - <change description>
    - <change description>

Where:
- `DD/MM/YY` is the current date (day/month/year, zero-padded)
- `HH:MM:SS` is the current time in the user's local timezone (24-hour, zero-padded)
- `<git_username>` is the output of `git config user.name`
- Each bullet describes one logical change with its **motivation or rationale** (e.g. "Fixed the bug where X caused Y", "Added missing Z required by W"), not just what was changed

### Rules

1. Append new entries to the **end** of the file (newest last)
2. Separate each entry from the previous one with a blank line and a horizontal rule (`---`)
3. If you make changes across multiple files, group related changes into a single entry
4. Do NOT edit or remove existing entries
5. Obtain the current date, time, and git username at the time you write the entry -- do not guess or reuse stale values
