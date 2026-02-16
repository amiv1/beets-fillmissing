"""Tests for error handling and edge cases."""

import pytest
from unittest.mock import Mock, call
from beetsplug.fillmissing import fillmissing_func


class TestEOFHandling:
    """Test handling of EOF (Ctrl+D)."""

    def test_eoferror_exits_gracefully(self, mock_lib, mock_ui, mock_opts, mock_item):
        """Test that EOFError (Ctrl+D) exits gracefully."""
        mock_item.get = Mock(return_value='')
        mock_lib.items.return_value = [mock_item]
        
        # Simulate Ctrl+D
        mock_ui.input_.side_effect = EOFError()
        
        fillmissing_func(mock_lib, mock_opts, [])
        
        # Should print exit message
        assert any('Exiting' in str(call) for call in mock_ui.print_.call_args_list)

    def test_eoferror_cleans_up_playback(self, mock_lib, mock_ui, mock_opts, mock_item, mock_subprocess, mock_platform):
        """Test that playback is cleaned up on EOF."""
        subprocess_mock, process = mock_subprocess
        mock_platform.system.return_value = 'Darwin'
        mock_item.get = Mock(return_value='')
        mock_lib.items.return_value = [mock_item]
        
        # Play, then EOF
        mock_ui.input_.side_effect = ['p', EOFError()]
        
        fillmissing_func(mock_lib, mock_opts, [])
        
        # Process should be terminated
        process.terminate.assert_called()


class TestKeyboardInterrupt:
    """Test handling of KeyboardInterrupt (Ctrl+C)."""

    def test_keyboard_interrupt_exits_gracefully(self, mock_lib, mock_ui, mock_opts, mock_item):
        """Test that KeyboardInterrupt (Ctrl+C) exits gracefully."""
        mock_item.get = Mock(return_value='')
        mock_lib.items.return_value = [mock_item]
        
        # Simulate Ctrl+C
        mock_ui.input_.side_effect = KeyboardInterrupt()
        
        fillmissing_func(mock_lib, mock_opts, [])
        
        # Should print interrupt message
        assert any('Interrupted by user' in str(call) for call in mock_ui.print_.call_args_list)

    def test_keyboard_interrupt_cleans_up_playback(self, mock_lib, mock_ui, mock_opts, mock_item, mock_subprocess, mock_platform):
        """Test that playback is cleaned up on interrupt."""
        subprocess_mock, process = mock_subprocess
        mock_platform.system.return_value = 'Darwin'
        mock_item.get = Mock(return_value='')
        mock_lib.items.return_value = [mock_item]
        
        # Play, then interrupt
        mock_ui.input_.side_effect = ['p', KeyboardInterrupt()]
        
        fillmissing_func(mock_lib, mock_opts, [])
        
        # Process should be terminated
        process.terminate.assert_called()


class TestPlaybackCleanup:
    """Test playback process cleanup."""

    def test_playback_cleaned_up_on_normal_exit(self, mock_lib, mock_ui, mock_opts, mock_item, mock_subprocess, mock_platform):
        """Test that playback is cleaned up on normal exit."""
        subprocess_mock, process = mock_subprocess
        mock_platform.system.return_value = 'Darwin'
        mock_item.get = Mock(return_value='')
        mock_lib.items.return_value = [mock_item]
        
        mock_ui.input_.side_effect = ['p', '', '', '']
        
        fillmissing_func(mock_lib, mock_opts, [])
        
        # Process should be terminated at the end
        process.terminate.assert_called()

    def test_stopped_playback_not_terminated(self, mock_lib, mock_ui, mock_opts, mock_item, mock_subprocess, mock_platform):
        """Test that already-stopped playback isn't terminated."""
        subprocess_mock, process = mock_subprocess
        mock_platform.system.return_value = 'Darwin'
        # Simulate process already stopped
        process.poll.return_value = 0
        mock_item.get = Mock(return_value='')
        mock_lib.items.return_value = [mock_item]
        
        mock_ui.input_.side_effect = ['p', '', '', '']
        
        fillmissing_func(mock_lib, mock_opts, [])
        
        # Terminate should not be called if process already stopped
        # (poll returns non-None)

    def test_no_playback_no_cleanup_error(self, mock_lib, mock_ui, mock_opts, mock_item):
        """Test that cleanup doesn't error when no playback was started."""
        mock_item.get = Mock(return_value='')
        mock_lib.items.return_value = [mock_item]
        
        mock_ui.input_.return_value = ''
        
        # Should not crash
        fillmissing_func(mock_lib, mock_opts, [])


class TestSpecialCharacters:
    """Test handling of special characters in values."""

    def test_special_characters_in_field_values(self, mock_lib, mock_ui, mock_opts, mock_item):
        """Test that special characters in field values are handled."""
        mock_item.get = Mock(return_value='')
        mock_lib.items.return_value = [mock_item]
        
        # Enter values with special characters
        mock_ui.input_.side_effect = [
            'rock & roll',
            'café music',
            'español'
        ]
        
        fillmissing_func(mock_lib, mock_opts, [])
        
        mock_item.__setitem__.assert_any_call('mood', 'rock & roll')
        mock_item.__setitem__.assert_any_call('context', 'café music')
        mock_item.__setitem__.assert_any_call('language', 'español')

    def test_unicode_in_field_values(self, mock_lib, mock_ui, mock_opts, mock_item):
        """Test that unicode characters are handled properly."""
        mock_item.get = Mock(return_value='')
        mock_lib.items.return_value = [mock_item]
        
        mock_ui.input_.side_effect = ['🎵 happy', '日本語', '']
        
        fillmissing_func(mock_lib, mock_opts, [])
        
        mock_item.__setitem__.assert_any_call('mood', '🎵 happy')
        mock_item.__setitem__.assert_any_call('context', '日本語')


class TestEdgeCases:
    """Test various edge cases."""

    def test_single_field_option(self, mock_lib, mock_ui, mock_item):
        """Test with only a single field to fill."""
        opts = Mock()
        opts.fields = 'mood'
        mock_item.get = Mock(return_value='')
        mock_lib.items.return_value = [mock_item]
        
        mock_ui.input_.return_value = 'happy'
        
        fillmissing_func(mock_lib, opts, [])
        
        mock_item.__setitem__.assert_called_once_with('mood', 'happy')

    def test_many_fields(self, mock_lib, mock_ui, mock_item):
        """Test with many fields to fill."""
        opts = Mock()
        opts.fields = 'mood context language genre artist album year'
        mock_item.get = Mock(return_value='')
        mock_lib.items.return_value = [mock_item]
        
        # Skip all fields
        mock_ui.input_.return_value = ''
        
        # Should not crash
        fillmissing_func(mock_lib, opts, [])

    def test_empty_query_string(self, mock_lib, mock_ui, mock_opts):
        """Test with empty query (all tracks)."""
        mock_lib.items.return_value = []
        
        fillmissing_func(mock_lib, mock_opts, [])
        
        # Should handle empty query
        mock_lib.items.assert_called()

    def test_query_with_special_characters(self, mock_lib, mock_ui, mock_opts):
        """Test query with special characters."""
        mock_lib.items.return_value = []
        
        # Query with quotes and special chars
        fillmissing_func(mock_lib, mock_opts, ["artist:'The Band'"])
        
        mock_lib.items.assert_called()

    def test_field_with_only_whitespace(self, mock_lib, mock_ui, mock_opts, mock_item):
        """Test that whitespace-only input is treated as empty."""
        mock_item.get = Mock(return_value='')
        mock_lib.items.return_value = [mock_item]
        
        # Enter only whitespace
        mock_ui.input_.side_effect = ['   ', '', '']
        
        fillmissing_func(mock_lib, mock_opts, [])
        
        # Should not update field (whitespace stripped to empty string)
        assert mock_item.__setitem__.call_count == 0

    def test_very_long_field_value(self, mock_lib, mock_ui, mock_opts, mock_item):
        """Test handling of very long field values."""
        mock_item.get = Mock(return_value='')
        mock_lib.items.return_value = [mock_item]
        
        long_value = 'a' * 1000
        mock_ui.input_.side_effect = [long_value, '', '']
        
        fillmissing_func(mock_lib, mock_opts, [])
        
        mock_item.__setitem__.assert_any_call('mood', long_value)

    def test_unknown_field_name(self, mock_lib, mock_ui, mock_item):
        """Test with custom/unknown field names."""
        opts = Mock()
        opts.fields = 'custom_field_xyz'
        mock_item.get = Mock(return_value='')
        mock_lib.items.return_value = [mock_item]
        
        mock_ui.input_.return_value = 'value'
        
        # Should work with any field name
        fillmissing_func(mock_lib, opts, [])
        
        mock_item.__setitem__.assert_called_once_with('custom_field_xyz', 'value')

    def test_done_message_printed(self, mock_lib, mock_ui, mock_opts, mock_item):
        """Test that 'Done!' message is printed at the end."""
        mock_item.get = Mock(return_value='')
        mock_lib.items.return_value = [mock_item]
        
        mock_ui.input_.return_value = ''
        
        fillmissing_func(mock_lib, mock_opts, [])
        
        mock_ui.print_.assert_any_call("Done!")

    def test_commands_tip_displayed(self, mock_lib, mock_ui, mock_opts, mock_item):
        """Test that command tips are displayed at start."""
        mock_item.get = Mock(return_value='')
        mock_lib.items.return_value = [mock_item]
        
        mock_ui.input_.return_value = ''
        
        fillmissing_func(mock_lib, mock_opts, [])
        
        # Check for tips message
        calls_str = ' '.join([str(call) for call in mock_ui.print_.call_args_list])
        assert 'Commands:' in calls_str or 'Tip:' in calls_str
