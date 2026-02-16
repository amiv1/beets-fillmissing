"""Core functionality tests for the fillmissing plugin."""

import pytest
from unittest.mock import Mock, call
from beetsplug.fillmissing import fillmissing_func


class TestBasicFunctionality:
    """Test basic plugin functionality."""

    def test_missing_fields_option_shows_error(self, mock_lib, mock_ui):
        """Test that missing -f option shows an error message."""
        opts = Mock()
        opts.fields = ''
        
        fillmissing_func(mock_lib, opts, [])
        
        mock_ui.print_.assert_any_call("Error: Please specify fields with -f option")
        mock_ui.print_.assert_any_call("Example: beet fillmissing 'query' -f 'language mood context'")

    def test_no_items_match_query(self, mock_lib, mock_ui, mock_opts):
        """Test behavior when query returns no results."""
        mock_lib.items.return_value = []
        
        fillmissing_func(mock_lib, mock_opts, ['artist:Unknown'])
        
        mock_ui.print_.assert_called_with("No items match the query.")

    def test_field_parsing_splits_on_spaces(self, mock_lib, mock_ui):
        """Test that fields are correctly parsed from space-separated string."""
        opts = Mock()
        opts.fields = 'mood context language genre'
        mock_lib.items.return_value = []
        
        fillmissing_func(mock_lib, opts, [])
        
        # Should get past field validation
        mock_ui.print_.assert_called_with("No items match the query.")

    def test_track_count_displayed(self, mock_lib, mock_ui, mock_opts, mock_items):
        """Test that correct track count is displayed."""
        items = mock_items(3)
        mock_lib.items.return_value = items
        mock_ui.input_.return_value = ''  # Skip all fields
        
        fillmissing_func(mock_lib, mock_opts, [])
        
        mock_ui.print_.assert_any_call("Found 3 track(s) matching query.")

    def test_track_info_displayed(self, mock_lib, mock_ui, mock_opts, mock_item):
        """Test that track information is correctly displayed."""
        mock_lib.items.return_value = [mock_item]
        mock_ui.input_.return_value = ''  # Skip all fields
        
        fillmissing_func(mock_lib, mock_opts, [])
        
        # Check track header and info displayed
        assert any('Track 1 of 1' in str(call) for call in mock_ui.print_.call_args_list)
        assert any('Test Track' in str(call) for call in mock_ui.print_.call_args_list)


class TestFieldUpdates:
    """Test field update functionality."""

    def test_update_empty_field_with_value(self, mock_lib, mock_ui, mock_opts, mock_item):
        """Test updating an empty field with a new value."""
        mock_item.get = Mock(return_value='')  # Empty field
        mock_lib.items.return_value = [mock_item]
        
        # Simulate user entering value for first field, then skipping rest
        mock_ui.input_.side_effect = ['chill', '', '']
        
        fillmissing_func(mock_lib, mock_opts, [])
        
        # Verify field was set
        mock_item.__setitem__.assert_any_call('mood', 'chill')
        mock_item.store.assert_called()
        mock_item.write.assert_called()
        mock_ui.print_.assert_any_call("    → Updated mood")

    def test_update_existing_field(self, mock_lib, mock_ui, mock_opts, mock_item):
        """Test updating a field that already has a value."""
        values = {'mood': 'happy', 'context': '', 'language': ''}
        mock_item.get = Mock(side_effect=lambda k, d='': values.get(k, d))
        mock_lib.items.return_value = [mock_item]
        
        # Update existing field
        mock_ui.input_.side_effect = ['energetic', '', '']
        
        fillmissing_func(mock_lib, mock_opts, [])
        
        mock_item.__setitem__.assert_any_call('mood', 'energetic')
        mock_item.store.assert_called()

    def test_skip_field_with_empty_input(self, mock_lib, mock_ui, mock_opts, mock_item):
        """Test that pressing Enter without input skips the field."""
        mock_item.get = Mock(return_value='')
        mock_lib.items.return_value = [mock_item]
        
        # Skip all fields by pressing Enter
        mock_ui.input_.return_value = ''
        
        fillmissing_func(mock_lib, mock_opts, [])
        
        # No fields should be updated
        assert mock_item.__setitem__.call_count == 0
        assert mock_item.store.call_count == 0

    def test_prompt_shows_existing_value(self, mock_lib, mock_ui, mock_opts, mock_item):
        """Test that prompt displays existing field value in brackets."""
        values = {'mood': 'chill', 'context': '', 'language': ''}
        mock_item.get = Mock(side_effect=lambda k, d='': values.get(k, d))
        mock_lib.items.return_value = [mock_item]
        
        mock_ui.input_.return_value = ''  # Skip all
        
        fillmissing_func(mock_lib, mock_opts, [])
        
        # Check that prompt includes existing value
        calls = [str(call) for call in mock_ui.input_.call_args_list]
        assert any('[chill]' in call for call in calls)

    def test_multiple_field_updates_on_single_track(self, mock_lib, mock_ui, mock_opts, mock_item):
        """Test updating multiple fields on a single track."""
        mock_item.get = Mock(return_value='')
        mock_lib.items.return_value = [mock_item]
        
        # Enter values for all three fields
        mock_ui.input_.side_effect = ['happy', 'workout', 'eng']
        
        fillmissing_func(mock_lib, mock_opts, [])
        
        # All three fields should be updated
        assert mock_item.__setitem__.call_count == 3
        mock_item.__setitem__.assert_any_call('mood', 'happy')
        mock_item.__setitem__.assert_any_call('context', 'workout')
        mock_item.__setitem__.assert_any_call('language', 'eng')
        assert mock_item.store.call_count == 3
        assert mock_item.write.call_count == 3

    def test_multiple_tracks_iteration(self, mock_lib, mock_ui, mock_opts, mock_items):
        """Test iterating through multiple tracks."""
        items = mock_items(2)
        mock_lib.items.return_value = items
        
        # Skip all fields for both tracks (3 fields × 2 tracks = 6 inputs)
        mock_ui.input_.return_value = ''
        
        fillmissing_func(mock_lib, mock_opts, [])
        
        # Should display both tracks
        calls_str = ' '.join([str(call) for call in mock_ui.print_.call_args_list])
        assert 'Track 1 of 2' in calls_str
        assert 'Track 2 of 2' in calls_str

    def test_whitespace_trimming(self, mock_lib, mock_ui, mock_opts, mock_item):
        """Test that input values are stripped of whitespace."""
        mock_item.get = Mock(return_value='')
        mock_lib.items.return_value = [mock_item]
        
        # Enter value with whitespace
        mock_ui.input_.side_effect = ['  happy  ', '', '']
        
        fillmissing_func(mock_lib, mock_opts, [])
        
        # Should be trimmed
        mock_item.__setitem__.assert_any_call('mood', 'happy')
