""" Watch job tests. """
import importlib
import logging
import sys

from pathlib import Path
from unittest.mock import MagicMock

import pytest


@pytest.fixture(name="watch")
def watch_module(monkeypatch):
    """Import the watch job, stubbing the Linux-only inotify package if needed"""
    try:
        import inotify.adapters  # pylint: disable=unused-import,import-outside-toplevel
    except ImportError:
        for name in ("inotify", "inotify.adapters", "inotify.constants"):
            monkeypatch.setitem(sys.modules, name, MagicMock())
        monkeypatch.delitem(sys.modules, "pyrosimple.job.watch", raising=False)
    return importlib.import_module("pyrosimple.job.watch")


def make_job(watch, available_methods, **config):
    job = watch.TreeWatch.__new__(watch.TreeWatch)
    job.name = "test"
    job.log = logging.getLogger(__name__)
    job.config = {
        "dry_run": False,
        "print_to_client": False,
        "preload_fields": [],
        "load_mode": "",
        "trust_resume": False,
        **config,
    }
    job.engine = MagicMock()
    job.engine.has_method.side_effect = lambda name: name in available_methods
    job.load_metafile_data = lambda _path: MagicMock()
    job.build_metafile_variables = lambda _path, _data: {
        "flags": set(),
        "commands": [],
    }
    return job


EDITED = {"load.verbose_edited", "load.start_verbose_edited"}


@pytest.mark.parametrize(
    ("config", "available", "expected"),
    [
        ({}, EDITED, "verbose"),
        ({"load_mode": "start"}, EDITED, "start_verbose"),
        ({"trust_resume": True}, EDITED, "verbose_edited"),
        ({"trust_resume": True, "load_mode": "start"}, EDITED, "start_verbose_edited"),
        # Older rTorrent without the *_edited commands
        ({"trust_resume": True}, set(), "verbose"),
        ({"trust_resume": True, "load_mode": "start"}, set(), "start_verbose"),
    ],
)
def test_load_metafile_trust_resume(watch, config, available, expected):
    job = make_job(watch, available, **config)
    job.load_metafile(Path("example.torrent"))

    load = job.engine.open.return_value.load
    getattr(load, expected).assert_called_once()
    for other in ("verbose", "start_verbose", "verbose_edited", "start_verbose_edited"):
        if other != expected:
            getattr(load, other).assert_not_called()
