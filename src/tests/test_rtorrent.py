# pylint: disable=
""" RTorrent tests.

    Copyright (c) 2011 The PyroScope Project <pyroscope.project@gmail.com>
"""
import logging
import unittest

from unittest.mock import Mock, call

import pytest

from box.box import Box

import pyrosimple

from pyrosimple import error
from pyrosimple.torrent import rtorrent
from pyrosimple.util.rpc import RTorrentProxy


@pytest.mark.parametrize(
    ("template", "fields"),
    [
        ("{{d.size}}", ["size"]),
        (
            "{{d.name|center}}{% if d.is_multi_file %}{{d.size}}{% endif %}",
            ["name", "size", "is_multi_file"],
        ),
    ],
)
def test_fields_from_template(template, fields):
    assert sorted(list(rtorrent.get_fields_from_template(template))) == sorted(fields)


def test_validate_field_list():
    assert rtorrent.validate_field_list("name,size") == ["name", "size"]
    assert rtorrent.validate_field_list("name.center,size.raw", True) == [
        "name.center",
        "size.raw",
    ]


def test_validate_sort_fields():
    rtorrent.validate_sort_fields("name,size")
    rtorrent.validate_sort_fields("name,-size")
    with pytest.raises(error.UserError):
        rtorrent.validate_sort_fields("very_fake_field")
    with pytest.raises(error.UserError):
        rtorrent.validate_sort_fields("very_fake_field.raw")
    with pytest.raises(error.UserError):
        rtorrent.validate_sort_fields("name.very_fake_filter")


def test_tag_add_then_remove_uses_fresh_rpc_value():
    class TagRpc:
        tags = ""

        def __getattr__(self, name):
            if name == "d.custom":
                return lambda _hash, _key: self.tags
            if name == "d.custom.set":
                return lambda _hash, _key, value: setattr(self, "tags", value)
            raise AttributeError(name)

    class TagEngine:
        def __init__(self):
            self.rpc = TagRpc()
            self.logger = logging.getLogger(__name__)

    engine = TagEngine()
    torrent = rtorrent.RtorrentItem(engine, {"hash": "A" * 40})
    torrent.tag("+review")
    torrent.tag("-review")

    assert engine.rpc.tags == ""


@pytest.fixture
def cull_engines(tmp_path):
    engines = [Mock(), Mock()]
    for engine in engines:
        getattr(engine.rpc, "d.directory").return_value = str(tmp_path / "data")
        getattr(engine.rpc, "d.is_multi_file").return_value = True
        getattr(engine.rpc, "d.tied_to_file").return_value = ""
        getattr(engine.rpc, "f.multicall").return_value = [["payload.bin"]]
    return engines


@pytest.fixture
def cull_engine(cull_engines):
    return cull_engines[0]


@pytest.mark.parametrize("remove_torrent", [True, False])
@pytest.mark.parametrize("method", ["cull", "purge"])
def test_cull_missing_directory(cull_engine, remove_torrent, method):
    torrent_hash = "A" * 40
    torrent = rtorrent.RtorrentItem(cull_engine, {"hash": torrent_hash})

    getattr(torrent, method)(remove_torrent=remove_torrent)

    if remove_torrent:
        getattr(cull_engine.rpc, "d.stop").assert_called_once_with(torrent_hash)
        getattr(cull_engine.rpc, "d.close").assert_called_once_with(torrent_hash)
        getattr(cull_engine.rpc, "d.erase").assert_called_once_with(torrent_hash)
    else:
        getattr(cull_engine.rpc, "d.stop").assert_not_called()
        getattr(cull_engine.rpc, "d.erase").assert_not_called()
    getattr(cull_engine.rpc, "f.multicall").assert_not_called()


@pytest.mark.parametrize("multi_file", [True, False])
@pytest.mark.parametrize("separate_clients", [True, False])
def test_cull_selected_torrents_sharing_directory(
    cull_engines, tmp_path, multi_file, separate_clients
):
    path = tmp_path / "data"
    path.mkdir()
    payload = path / "payload.bin"
    payload.write_bytes(b"shared payload")
    first_engine, second_engine = cull_engines
    if not separate_clients:
        second_engine = first_engine
    for engine in cull_engines:
        getattr(engine.rpc, "d.is_multi_file").return_value = multi_file
    torrents = [
        rtorrent.RtorrentItem(first_engine, {"hash": "A" * 40}),
        rtorrent.RtorrentItem(second_engine, {"hash": "B" * 40}),
        rtorrent.RtorrentItem(first_engine, {"hash": "C" * 40}),
    ]

    for torrent in torrents[:2]:
        torrent.cull()

    assert not payload.exists()
    assert path.exists() == (not multi_file)
    if separate_clients:
        getattr(first_engine.rpc, "d.erase").assert_called_once_with("A" * 40)
        getattr(second_engine.rpc, "d.erase").assert_called_once_with("B" * 40)
    else:
        assert getattr(first_engine.rpc, "d.erase").call_args_list == [
            call("A" * 40),
            call("B" * 40),
        ]


def test_cull_preserves_untracked_files(cull_engine, tmp_path):
    path = tmp_path / "data"
    path.mkdir()
    payload = path / "payload.bin"
    payload.write_bytes(b"shared payload")
    untracked = path / "untracked.bin"
    untracked.write_bytes(b"unrelated data")
    torrents = [
        rtorrent.RtorrentItem(cull_engine, {"hash": char * 40}) for char in ("A", "B")
    ]

    for torrent in torrents:
        torrent.cull()

    assert not payload.exists()
    assert untracked.read_bytes() == b"unrelated data"
    assert getattr(cull_engine.rpc, "d.erase").call_args_list == [
        call("A" * 40),
        call("B" * 40),
    ]


class MockProxy:
    def log(self, *_):
        pass

    def d_multicall2(self, _, _viewname, *fields):
        print(_viewname)
        print(fields)
        ret_items = []
        for f in fields:
            ret_items.append([i[f] for i in self.items])
        return ret_items

    def d_name(self, hash):
        for i in items:
            if i["d.hash="] == hash:
                return i["d.name="]

    def __init__(self):
        self.d = Box(
            multicall2=self.d_multicall2,
            name=self.d_name,
        )
        self.items = [
            {
                "d.name=": "Test.Item",
                "d.hash=": "A" * 40,
            }
        ]


def test_rpc():
    e = pyrosimple.connect("localhost:8080")
    e.rpc = MockProxy()
    e.properties = {"foo": "bar"}
    e.log("test")
    items = list(e.items("default", ["d.name"]))
