# beets-fillmissing

A [Beets](https://beets.io/) plugin that interactively prompts you to fill in missing or incomplete metadata fields for your music tracks.

## Features

- 🎯 **Query-based workflow**: Target specific tracks using Beets' powerful query syntax
- 📝 **Interactive prompts**: Fill in metadata fields one by one with clear visual feedback
- 🔄 **Smart defaults**: Existing field values are shown as defaults - just press Enter to keep them
- 🎵 **Built-in playback**: Type `p` or `play` to listen to a track before filling in metadata
- ✅ **Immediate writes**: Changes are saved immediately after each field update
- ⚡ **Fast workflow**: Skip fields with Enter, exit anytime with Ctrl+C or Ctrl+D

## Installation

### From Git (Recommended)

Install directly from GitHub:

```bash
# Using pip
pip install git+https://github.com/amiv1/beets-fillmissing.git

# Using pipx
pipx inject beets git+https://github.com/amiv1/beets-fillmissing.git
```

## Configuration

Add `fillmissing` to your plugins in Beets config file (usually `~/.config/beets/config.yaml`):

```yaml
plugins:
  - fillmissing
  # ... other plugins
```

## Usage

```bash
beet fillmissing [QUERY] -f 'field1 field2 field3'
```

### Arguments

- `QUERY`: Standard Beets query to filter tracks (e.g., `artist:Unknown`, `genre:Hip-Hop`, `album:'My Album'`)
- `-f, --fields`: Space-separated list of fields to populate

### Examples

Add genre and mood tags to tracks in a specific album:
```bash
beet fillmissing 'album:Chill Vibes' -f 'genre mood'
```

Add mood tags for tracks that don't have it:
```bash
beet fillmissing '^mood::.+' -f 'mood'
```

## Interactive Commands

While filling in metadata, you can:

- **Enter a value**: Type the new value and press Enter to update the field
- **Skip a field**: Press Enter without typing to skip (keeps existing value or leaves blank)
- **Play track**: Type `p` to open the track in your system's default audio player
- **Go back**: Type `b` to go back to editing the previous field
- **Skip track**: Type `s` to skip the current track metadata editing and go to the next one
- **Exit**: Press Ctrl+C or Ctrl+D to stop the process anytime

## Example Session

```
$ beet fillmissing 'mood:' -f 'mood context language'
Found 3 track(s) matching query.
Commands: 'p' = play | 's' = skip track | 'b' = back | Ctrl+C = quit

--- Track 1 of 3 ---
Jazz Ensemble - Smooth Jazz Collection - Summer Breeze

  mood: chill
    → Updated mood
  context [driving]: workout
    → Updated context
  language: eng
    → Updated language

--- Track 2 of 3 ---
Synthwave Artists - Neon Nights - Midnight Drive

  mood: p
    ♪ Playing...
  mood: energy
    → Updated mood
  context: driving
    → Updated context
  language: 

--- Track 3 of 3 ---
...

Done!
```

## Field Behavior

- **Existing values**: If a field already has a value, it's shown in brackets `[current_value]`
  - Press Enter to keep it unchanged
  - Type a new value to replace it

- **Empty fields**: If a field is blank or doesn't exist, no default is shown
  - Press Enter to skip without setting anything
  - Type a value to set the field

## Contributing

Issues and pull requests are welcome!
