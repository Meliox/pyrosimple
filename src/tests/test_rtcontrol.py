import multiprocessing.pool
import threading

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from pyrosimple import config
from pyrosimple.scripts.rtcontrol import RtorrentControl


@pytest.mark.parametrize("fail_fetch", [False, True])
def test_threaded_fetch_without_multiprocessing(monkeypatch, fail_fetch):
    def reject_multiprocessing():
        pytest.fail("Threaded result fetching must not initialize multiprocessing")

    monkeypatch.setattr(multiprocessing.pool, "get_context", reject_multiprocessing)
    monkeypatch.setattr(config, "load_custom_py", lambda: None)
    control = RtorrentControl()
    control.args = ["--yes", "--stop", "-o", "-", "--sort", "name", "name=*"]
    control.get_options()
    barrier = threading.Barrier(2)
    workers = []
    actions = []
    engines = {}
    for name in ("first", "second"):
        item = SimpleNamespace(name=name, stop=lambda n=name: actions.append(n))
        engine = Mock()
        engine.view.return_value.size.return_value = 1

        def fetch(*, view, prefetch, item=item):
            workers.append(threading.current_thread())
            barrier.wait(timeout=5)
            if fail_fetch and item.name == "first":
                raise RuntimeError("fetch failed")
            return [item]

        engine.items.side_effect = fetch
        engines[name] = engine

    def open_engines():
        control.engines = engines
        return engines

    monkeypatch.setattr(control, "open", open_engines)
    if fail_fetch:
        with pytest.raises(RuntimeError, match="fetch failed"):
            control.mainloop()
        assert actions == []
    else:
        control.mainloop()
        assert actions == ["first", "second"]
    assert len(workers) == 2
    assert all(not worker.is_alive() for worker in workers)
