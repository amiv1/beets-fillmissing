"""Tests for special commands (play, skip, back)."""

import pytest
from unittest.mock import Mock, call
from beetsplug.fillmissing import fillmissing_func


class TestPlayCommand:
    """Test the play command functionality."""

    def test_play_command_lowercase_p(self, mock_lib, mock_ui, mock_opts, mock_item, mock_subprocess, mock_platform):
        """Test that 'p' triggers playback."""
        subprocess_mock, process = mock_subprocess
        mock_platform.system.return_value = 'Darwin'
        mock_item.get = Mock(return_value='')
        mock_lib.items.return_value = [mock_item]
        
        # User types 'p' then a value, then skips rest
        mock_ui.input_.side_effect = ['p', 'happy', '', '']
        
        fillmissing_func(mock_lib, mock_opts, [])
        
        subprocess_mock.Popen.assert_called()
        mock_ui.print_.assert_any_call("    ♪ Playing...")

    def test_play_command_macos(self, mock_lib, mock_ui, mock_opts, mock_item, mock_subprocess, mock_platform):
        """Test play command uses 'open' on macOS."""
        subprocess_mock, process = mock_subprocess
        mock_platform.system.return_value = 'Darwin'
        mock_item.path = b'/path/to/song.mp3'
        mock_item.get = Mock(return_value='')
        mock_lib.items.return_value = [mock_item]
        
        mock_ui.input_.side_effect = ['p', '', '', '']
        
        fillmissing_func(mock_lib, mock_opts, [])
        
        # Check that 'open' command was used
        call_args = subprocess_mock.Popen.call_args
        assert 'open' in call_args[0][0]
        assert '/path/to/song.mp3' in call_args[0][0]

    def test_play_command_windows(self, mock_lib, mock_ui, mock_opts, mock_item, mock_subprocess, mock_platform):
        """Test play command uses 'start' on Windows."""
        subprocess_mock, process = mock_subprocess
        mock_platform.system.return_value = 'Windows'
        mock_item.path = b'C:\\Music\\song.mp3'
        mock_item.get = Mock(return_value='')
        mock_lib.items.return_value = [mock_item]
        
        mock_ui.input_.side_effect = ['p', '', '', '']
        
        fillmissing_func(mock_lib, mock_opts, [])
        
        # Check that start command was used with shell=True
        call_kwargs = subprocess_mock.Popen.call_args[1]
        assert call_kwargs['shell'] is True

    def test_play_command_linux(self, mock_lib, mock_ui, mock_opts, mock_item, mock_subprocess, mock_platform):
        """Test play command uses 'xdg-open' on Linux."""
        subprocess_mock, process = mock_subprocess
        mock_platform.system.return_value = 'Linux'
        mock_item.path = b'/home/user/music/song.mp3'
        mock_item.get = Mock(return_value='')
        mock_lib.items.return_value = [mock_item]
        
        mock_ui.input_.side_effect = ['p', '', '', '']
        
        fillmissing_func(mock_lib, mock_opts, [])
        
        # Check that xdg-open was used
        call_args = subprocess_mock.Popen.call_args
        assert 'xdg-open' in call_args[0][0]

    def test_play_command_stops_previous_playback(self, mock_lib, mock_ui, mock_opts, mock_item, mock_subprocess, mock_platform):
        """Test that playing again stops the previous playback."""
        subprocess_mock, process = mock_subprocess
        mock_platform.system.return_value = 'Darwin'
        mock_item.get = Mock(return_value='')
        mock_lib.items.return_value = [mock_item]
        
        # Play twice in a row
        mock_ui.input_.side_effect = ['p', 'p', '', '', '']
        
        fillmissing_func(mock_lib, mock_opts, [])
        
        # Previous process should be terminated
        assert process.terminate.call_count >= 1

    def test_play_command_doesnt_advance_field(self, mock_lib, mock_ui, mock_opts, mock_item, mock_subprocess, mock_platform):
        """Test that play command doesn't advance to next field."""
        subprocess_mock, process = mock_subprocess
        mock_platform.system.return_value = 'Darwin'
        mock_item.get = Mock(return_value='')
        mock_lib.items.return_value = [mock_item]
        
        # Type 'p' to play, then enter value for same field
        mock_ui.input_.side_effect = ['p', 'happy', '', '']
        
        fillmissing_func(mock_lib, mock_opts, [])
        
        # Should still update the mood field (first field)
        mock_item.__setitem__.assert_any_call('mood', 'happy')

    def test_play_command_error_handling(self, mock_lib, mock_ui, mock_opts, mock_item, mock_subprocess, mock_platform):
        """Test that playback errors are handled gracefully."""
        subprocess_mock, process = mock_subprocess
        mock_platform.system.return_value = 'Darwin'
        subprocess_mock.Popen.side_effect = Exception("Cannot open file")
        mock_item.get = Mock(return_value='')
        mock_lib.items.return_value = [mock_item]
        
        mock_ui.input_.side_effect = ['p', '', '', '']
        
        # Should not crash
        fillmissing_func(mock_lib, mock_opts, [])
        
        # Error message should be shown
        assert any('Could not play track' in str(call) for call in mock_ui.print_.call_args_list)

    def test_play_command_case_insensitive(self, mock_lib, mock_ui, mock_opts, mock_item, mock_subprocess, mock_platform):
        """Test that 'P' (uppercase) also triggers playback."""
        subprocess_mock, process = mock_subprocess
        mock_platform.system.return_value = 'Darwin'
        mock_item.get = Mock(return_value='')
        mock_lib.items.return_value = [mock_item]
        
        mock_ui.input_.side_effect = ['P', '', '', '']
        
        fillmissing_func(mock_lib, mock_opts, [])
        
        subprocess_mock.Popen.assert_called()


class TestSkipCommand:
    """Test the skip track command."""

    def test_skip_command_lowercase_s(self, mock_lib, mock_ui, mock_opts, mock_items):
        """Test that 's' skips to next track."""
        items = mock_items(2)
        mock_lib.items.return_value = items
        
        # Skip first track with 's', then skip all fields on second track
        mock_ui.input_.side_effect = ['s', '', '', '']
        
        fillmissing_func(mock_lib, mock_opts, [])
        
        # Should see skip message
        mock_ui.print_.assert_any_call("    → Skipping track")
        
        # Should still process second track
        calls_str = ' '.join([str(call) for call in mock_ui.print_.call_args_list])
        assert 'Track 2 of 2' in calls_str

    def test_skip_command_uppercase(self, mock_lib, mock_ui, mock_opts, mock_items):
        """Test that 'S' (uppercase) also skips track."""
        items = mock_items(2)
        mock_lib.items.return_value = items
        
        mock_ui.input_.side_effect = ['S', '', '', '']
        
        fillmissing_func(mock_lib, mock_opts, [])
        
        mock_ui.print_.assert_any_call("    → Skipping track")

    def test_skip_command_no_field_updates(self, mock_lib, mock_ui, mock_opts, mock_items):
        """Test that skip command doesn't update any fields on that track."""
        items = mock_items(1)
        mock_lib.items.return_value = items
        
        mock_ui.input_.side_effect = ['s']
        
        fillmissing_func(mock_lib, mock_opts, [])
        
        # No fields should be updated
        assert items[0].__setitem__.call_count == 0


class TestBackCommand:
    """Test the back command functionality."""

    def test_back_command_lowercase_b(self, mock_lib, mock_ui, mock_opts, mock_item):
        """Test that 'b' goes back to previous field."""
        mock_item.get = Mock(return_value='')
        mock_lib.items.return_value = [mock_item]
        
        # Enter first field, go back, enter it again, skip rest
        mock_ui.input_.side_effect = ['happy', 'b', 'chill', '', '']
        
        fillmissing_func(mock_lib, mock_opts, [])
        
        mock_ui.print_.assert_any_call("    ← Going back")
        # Should update first field with 'chill' (second attempt)
        mock_item.__setitem__.assert_any_call('mood', 'chill')

    def test_back_command_at_first_field(self, mock_lib, mock_ui, mock_opts, mock_item):
        """Test that back command at first field shows error message."""
        mock_item.get = Mock(return_value='')
        mock_lib.items.return_value = [mock_item]
        
        # Try to go back at first field
        mock_ui.input_.side_effect = ['b', '', '', '']
        
        fillmissing_func(mock_lib, mock_opts, [])
        
        mock_ui.print_.assert_any_call("    ✗ Already at first field")

    def test_back_command_uppercase(self, mock_lib, mock_ui, mock_opts, mock_item):
        """Test that 'B' (uppercase) also goes back."""
        mock_item.get = Mock(return_value='')
        mock_lib.items.return_value = [mock_item]
        
        mock_ui.input_.side_effect = ['test', 'B', 'test2', '', '']
        
        fillmissing_func(mock_lib, mock_opts, [])
        
        mock_ui.print_.assert_any_call("    ← Going back")

    def test_back_command_navigation_flow(self, mock_lib, mock_ui, mock_opts, mock_item):
        """Test navigating back through multiple fields."""
        mock_item.get = Mock(return_value='')
        mock_lib.items.return_value = [mock_item]
        
        # Fill 2 fields, go back once, refill
        mock_ui.input_.side_effect = [
            'happy',     # mood = happy
            'workout',   # context = workout
            'b',         # back to context
            'driving',   # context = driving (overwrite)
            'eng'        # language = eng
        ]
        
        fillmissing_func(mock_lib, mock_opts, [])
        
        # Final values: mood=happy, context=driving (updated), language=eng
        calls = mock_item.__setitem__.call_args_list
        assert call('mood', 'happy') in calls
        assert call('context', 'driving') in calls
        assert call('language', 'eng') in calls


class TestPathEncoding:
    """Test handling of byte vs string paths."""

    def test_bytes_path_decoded(self, mock_lib, mock_ui, mock_opts, mock_item, mock_subprocess, mock_platform):
        """Test that byte paths are decoded to strings for playback."""
        subprocess_mock, process = mock_subprocess
        mock_platform.system.return_value = 'Darwin'
        mock_item.path = b'/path/to/song.mp3'
        mock_item.get = Mock(return_value='')
        mock_lib.items.return_value = [mock_item]
        
        mock_ui.input_.side_effect = ['p', '', '', '']
        
        fillmissing_func(mock_lib, mock_opts, [])
        
        # Path should be decoded
        call_args = subprocess_mock.Popen.call_args
        path_in_call = str(call_args)
        assert '/path/to/song.mp3' in path_in_call

    def test_string_path_used_directly(self, mock_lib, mock_ui, mock_opts, mock_item, mock_subprocess, mock_platform):
        """Test that string paths are used directly."""
        subprocess_mock, process = mock_subprocess
        mock_platform.system.return_value = 'Darwin'
        mock_item.path = '/path/to/song.mp3'  # String, not bytes
        mock_item.get = Mock(return_value='')
        mock_lib.items.return_value = [mock_item]
        
        mock_ui.input_.side_effect = ['p', '', '', '']
        
        fillmissing_func(mock_lib, mock_opts, [])
        
        subprocess_mock.Popen.assert_called()
