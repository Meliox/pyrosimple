# pylint: disable=
""" XMLRPC tests.

    Copyright (c) 2011 The PyroScope Project <pyroscope.project@gmail.com>
"""
import logging
import unittest
import xmlrpc.client

import pytest

from pyrosimple.util import rpc


@pytest.mark.parametrize(
    "url",
    [
        "scgi://example.com:7000",
        "scgi:///var/tmp/rtorrent.sock",
        "http://example.com:7000",
        "http://example.com:7000?rpc=json",
        "http://example.com:7000/RPC3",
        "scgi+ssh://example.com:7000/RPC3",
    ],
)
def test_rpc_url(url):
    rpc.RTorrentProxy(url)


def test_missing_hash_fault():
    fault_message = "invalid parameters: info-hash not found"

    class FaultTransport:
        def request(self, *_args, **_kwargs):
            raise xmlrpc.client.Fault(-503, fault_message)

    proxy = rpc.RTorrentProxy(
        "scgi+unix:///tmp/rtorrent.sock", transport=FaultTransport()
    )

    with pytest.raises(rpc.HashNotFound) as raised:
        proxy.d.name("A" * 40)

    assert raised.value.faultCode == -503
