"""Pytest fixtures and configuration for beets-fillmissing tests."""

import pytest
from unittest.mock import Mock, MagicMock


@pytest.fixture
def mock_lib():
    """Mock beets library object."""
    lib = Mock()
    lib.items = Mock()
    return lib


@pytest.fixture
def mock_item():
    """Mock beets item (track) object."""
    item = MagicMock()
    item.path = b'/path/to/track.mp3'
    item.get = Mock(side_effect=lambda key, default='': {
        'title': 'Test Track',
        'artist': 'Test Artist',
        'album': 'Test Album',
    }.get(key, default))
    item.__getitem__ = Mock(side_effect=lambda key: {
        'title': 'Test Track',
        'artist': 'Test Artist',
        'album': 'Test Album',
    }.get(key, ''))
    item.__setitem__ = Mock()
    item.store = Mock()
    item.write = Mock()
    return item


@pytest.fixture
def mock_items(mock_item):
    """Create multiple mock items."""
    def create_items(count=3):
        items = []
        for i in range(count):
            item = MagicMock()
            item.path = f'/path/to/track{i}.mp3'.encode()
            item.get = Mock(side_effect=lambda key, default='', idx=i: {
                'title': f'Track {idx + 1}',
                'artist': f'Artist {idx + 1}',
                'album': f'Album {idx + 1}',
            }.get(key, default))
            item.__getitem__ = Mock(side_effect=lambda key, idx=i: {
                'title': f'Track {idx + 1}',
                'artist': f'Artist {idx + 1}',
                'album': f'Album {idx + 1}',
            }.get(key, ''))
            item.__setitem__ = Mock()
            item.store = Mock()
            item.write = Mock()
            items.append(item)
        return items
    return create_items


@pytest.fixture
def mock_opts():
    """Mock command options object."""
    opts = Mock()
    opts.fields = 'mood context language'
    return opts


@pytest.fixture
def mock_ui(mocker):
    """Mock beets UI module."""
    ui_mock = mocker.patch('beetsplug.fillmissing.ui')
    ui_mock.print_ = Mock()
    ui_mock.input_ = Mock()
    return ui_mock


@pytest.fixture
def mock_subprocess(mocker):
    """Mock subprocess module."""
    subprocess_mock = mocker.patch('beetsplug.fillmissing.subprocess')
    process = Mock()
    process.poll = Mock(return_value=None)
    process.terminate = Mock()
    process.wait = Mock()
    subprocess_mock.Popen = Mock(return_value=process)
    subprocess_mock.DEVNULL = Mock()
    return subprocess_mock, process


@pytest.fixture
def mock_platform(mocker):
    """Mock platform module."""
    return mocker.patch('beetsplug.fillmissing.platform')
