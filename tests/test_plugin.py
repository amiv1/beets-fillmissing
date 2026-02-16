"""Tests for plugin integration with Beets."""

import pytest
from beetsplug.fillmissing import FillMissingPlugin, fill_missing_command


class TestPluginIntegration:
    """Test plugin registration and integration."""

    def test_plugin_returns_commands(self):
        """Test that plugin returns list of commands."""
        plugin = FillMissingPlugin()
        commands = plugin.commands()
        
        assert isinstance(commands, list)
        assert len(commands) == 1

    def test_plugin_returns_fillmissing_command(self):
        """Test that plugin returns the fillmissing command."""
        plugin = FillMissingPlugin()
        commands = plugin.commands()
        
        assert fill_missing_command in commands

    def test_command_has_correct_name(self):
        """Test that command has correct name."""
        assert fill_missing_command.name == 'fillmissing'

    def test_command_has_help_text(self):
        """Test that command has help text."""
        assert fill_missing_command.help is not None
        assert len(fill_missing_command.help) > 0
        assert 'metadata' in fill_missing_command.help.lower()

    def test_command_has_func(self):
        """Test that command has a function assigned."""
        assert fill_missing_command.func is not None
        assert callable(fill_missing_command.func)

    def test_command_parser_exists(self):
        """Test that command has a parser."""
        assert fill_missing_command.parser is not None

    def test_fields_option_exists(self):
        """Test that -f/--fields option exists."""
        parser = fill_missing_command.parser
        
        # Check that the parser has the fields option
        # Note: This depends on optparse internals
        has_fields_option = any(
            opt.dest == 'fields'
            for opt in parser.option_list
        )
        assert has_fields_option

    def test_fields_option_short_form(self):
        """Test that -f short form exists."""
        parser = fill_missing_command.parser
        
        has_f_flag = any(
            '-f' in opt._short_opts if hasattr(opt, '_short_opts') else False
            for opt in parser.option_list
        )
        assert has_f_flag

    def test_fields_option_long_form(self):
        """Test that --fields long form exists."""
        parser = fill_missing_command.parser
        
        has_fields_flag = any(
            '--fields' in opt._long_opts if hasattr(opt, '_long_opts') else False
            for opt in parser.option_list
        )
        assert has_fields_flag

    def test_fields_option_default_empty(self):
        """Test that fields option defaults to empty string."""
        parser = fill_missing_command.parser
        options, _ = parser.parse_args([])
        
        assert options.fields == ''

    def test_fields_option_can_be_set(self):
        """Test that fields option can be set via command line."""
        parser = fill_missing_command.parser
        options, _ = parser.parse_args(['-f', 'mood context'])
        
        assert options.fields == 'mood context'

    def test_fields_option_help_text(self):
        """Test that fields option has help text."""
        parser = fill_missing_command.parser
        
        fields_option = next(
            opt for opt in parser.option_list
            if opt.dest == 'fields'
        )
        
        assert fields_option.help is not None
        assert len(fields_option.help) > 0
