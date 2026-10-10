# pylint: disable=
""" RTorrent tests.

    Copyright (c) 2011 The PyroScope Project <pyroscope.project@gmail.com>
"""
import logging
import unittest

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
