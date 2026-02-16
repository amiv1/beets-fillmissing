from beets.plugins import BeetsPlugin
from beets.ui import Subcommand, decargs
from beets import ui
import subprocess


def fillmissing_func(lib, opts, args):
    """Interactively fill missing metadata fields for tracks."""

    # Parse arguments
    query = decargs(args)
    fields = opts.fields

    # Validate fields option
    if not fields:
        ui.print_("Error: Please specify fields with -f option")
        ui.print_("Example: beet fillmissing 'query' -f 'language mood context'")
        return

    # Split fields string into list
    field_list = fields.split()

    # Execute query
    items = lib.items(query)
    items_list = list(items)

    if not items_list:
        ui.print_("No items match the query.")
        return

    total_tracks = len(items_list)
    ui.print_(f"Found {total_tracks} track(s) matching query.")
    ui.print_("Tip: Type 'p' or 'play' to listen to the track\n")

    # Iterate through items
    current_playback = None
    try:
        for idx, item in enumerate(items_list, 1):
            # Display track info
            title = item.get('title', 'Unknown Title')
            artist = item.get('artist', 'Unknown Artist')
            album = item.get('album', 'Unknown Album')

            ui.print_(f"--- Track {idx} of {total_tracks} ---")
            ui.print_(f"{title} by {artist} ({album})")
            ui.print_("")

            # Prompt for each field
            field_idx = 0
            while field_idx < len(field_list):
                field = field_list[field_idx]
                current_value = item.get(field, '')

                # Build prompt
                if current_value:
                    prompt_text = f"  {field} [{current_value}]: "
                else:
                    prompt_text = f"  {field}: "

                # Get user input
                try:
                    user_input = ui.input_(prompt_text)
                except EOFError:
                    # Handle Ctrl+D
                    ui.print_("\n\nExiting.")
                    if current_playback:
                        current_playback.terminate()
                    return

                # Check for playback command
                if user_input.strip().lower() in ['p', 'play']:
                    # Stop previous playback if any
                    if current_playback:
                        current_playback.terminate()

                    # Start playback with system default player
                    file_path = item.path.decode('utf-8') if isinstance(item.path, bytes) else item.path
                    try:
                        current_playback = subprocess.Popen(
                            ['open', file_path],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                        ui.print_("    ♪ Playing...")
                    except Exception as e:
                        ui.print_(f"    ✗ Could not play track: {e}")

                    # Don't advance field, let user enter value again
                    continue

                # Process input
                if user_input.strip():
                    # User entered a value - update field
                    item[field] = user_input.strip()
                    item.store()
                    item.write()
                    ui.print_(f"    → Updated {field}")
                # If empty input, skip (keep existing value or leave blank)

                field_idx += 1

            ui.print_("")  # Blank line between tracks

    except KeyboardInterrupt:
        ui.print_("\n\nInterrupted by user.")
        if current_playback:
            current_playback.terminate()
        return

    # Clean up playback on exit
    if current_playback:
        current_playback.terminate()

    ui.print_("Done!")


fill_missing_command = Subcommand(
    "fillmissing", 
    help="Fill missing metadata interactively"
)
fill_missing_command.parser.add_option(
    '-f', '--fields',
    dest='fields',
    default='',
    help='space-separated list of fields to populate'
)
fill_missing_command.func = fillmissing_func


class FillMissingPlugin(BeetsPlugin):
    def commands(self):
        return [fill_missing_command]
