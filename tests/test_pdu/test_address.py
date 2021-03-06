#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Nose Test PDU Address
---------------------
"""

import unittest

from bacpypes.debugging import bacpypes_debugging, ModuleLogger, xtob
from bacpypes.pdu import Address, LocalStation, RemoteStation, \
    LocalBroadcast, RemoteBroadcast, GlobalBroadcast

# some debugging
_debug = 0
_log = ModuleLogger(globals())


@bacpypes_debugging
class MatchAddressMixin:

    def match_address(self, addr, t, n, l, a):
        """Assert that the type, network, length, and address are what
        they should be.  Note that the address parameter is a hex string
        that will be converted to bytes for comparison.

        :param addr: the address to match
        :param t: the address type
        :param n: the network number
        :param l: the address length
        :param a: the address expressed as hex bytes
        """
        if _debug:
            MatchAddressMixin._debug("match_address %r %r %r %r %r",
                addr, t, n, l, a,
            )

        assert addr.addrType == t
        assert addr.addrNet == n
        assert addr.addrLen == l
        if a is None:
            assert addr.addrAddr is None
        else:
            assert addr.addrAddr == xtob(a)


@bacpypes_debugging
class TestAddress(unittest.TestCase, MatchAddressMixin):

    def test_address(self):
        if _debug: TestAddress._debug("test_address")

        # null address
        test_addr = Address()
        self.match_address(test_addr, 0, None, 0, '')
        assert str(test_addr) == "Null"

    def test_address_int(self):
        if _debug: TestAddress._debug("test_address_int")

        # test integer local station
        test_addr = Address(1)
        self.match_address(test_addr, 2, None, 1, '01')
        assert str(test_addr) == "1"

        test_addr = Address(254)
        self.match_address(test_addr, 2, None, 1, 'fe')
        assert str(test_addr) == "254"

        # test bad integer
        with self.assertRaises(ValueError):
            Address(-1)
        with self.assertRaises(ValueError):
            Address(256)

    def test_address_ipv4(self):
        if _debug: TestAddress._debug("test_address_ipv4")

        # test IPv4 local station address
        test_addr = Address("1.2.3.4")
        self.match_address(test_addr, 2, None, 6, '01020304BAC0')
        assert str(test_addr) == "1.2.3.4"

        # test IPv4 local station address with non-standard port
        test_addr = Address("1.2.3.4:47809")
        self.match_address(test_addr, 2, None, 6, '01020304BAC1')
        assert str(test_addr) == "1.2.3.4:47809"

        # test IPv4 local station address with unrecognized port
        test_addr = Address("1.2.3.4:47999")
        self.match_address(test_addr, 2, None, 6, '01020304bb7f')
        assert str(test_addr) == "0x01020304bb7f"

    def test_address_eth(self):
        if _debug: TestAddress._debug("test_address_eth")

        # test Ethernet local station address
        test_addr = Address("01:02:03:04:05:06")
        self.match_address(test_addr, 2, None, 6, '010203040506')
        assert str(test_addr) == "0x010203040506"

    def test_address_local_station(self):
        if _debug: TestAddress._debug("test_address_local_station")

        # test integer local station
        test_addr = Address("1")
        self.match_address(test_addr, 2, None, 1, '01')
        assert str(test_addr) == "1"

        test_addr = Address("254")
        self.match_address(test_addr, 2, None, 1, 'fe')
        assert str(test_addr) == "254"

        # test bad integer string
        with self.assertRaises(ValueError):
            Address("256")

        # test modern hex string
        test_addr = Address("0x01")
        self.match_address(test_addr, 2, None, 1, '01')
        assert str(test_addr) == "1"

        test_addr = Address("0x0102")
        self.match_address(test_addr, 2, None, 2, '0102')
        assert str(test_addr) == "0x0102"

        # test old school hex string
        test_addr = Address("X'01'")
        self.match_address(test_addr, 2, None, 1, '01')
        assert str(test_addr) == "1"

        test_addr = Address("X'0102'")
        self.match_address(test_addr, 2, None, 2, '0102')
        assert str(test_addr) == "0x0102"

    def test_address_local_broadcast(self):
        if _debug: TestAddress._debug("test_address_local_broadcast")

        # test local broadcast
        test_addr = Address("*")
        self.match_address(test_addr, 1, None, None, None)
        assert str(test_addr) == "*"

    def test_address_remote_broadcast(self):
        if _debug: TestAddress._debug("test_address_remote_broadcast")

        # test remote broadcast
        test_addr = Address("1:*")
        self.match_address(test_addr, 3, 1, None, None)
        assert str(test_addr) == "1:*"

        # test remote broadcast bad network
        with self.assertRaises(ValueError):
            Address("65536:*")

    def test_address_remote_station(self):
        if _debug: TestAddress._debug("test_address_remote_station")

        # test integer remote station
        test_addr = Address("1:2")
        self.match_address(test_addr, 4, 1, 1, '02')
        assert str(test_addr) == "1:2"

        test_addr = Address("1:254")
        self.match_address(test_addr, 4, 1, 1, 'fe')
        assert str(test_addr) == "1:254"

        # test bad network and node
        with self.assertRaises(ValueError):
            Address("65536:2")
        with self.assertRaises(ValueError):
            Address("1:256")

        # test modern hex string
        test_addr = Address("1:0x02")
        self.match_address(test_addr, 4, 1, 1, '02')
        assert str(test_addr) == "1:2"

        # test bad network
        with self.assertRaises(ValueError):
            Address("65536:0x02")

        test_addr = Address("1:0x0203")
        self.match_address(test_addr, 4, 1, 2, '0203')
        assert str(test_addr) == "1:0x0203"

        # test old school hex string
        test_addr = Address("1:X'02'")
        self.match_address(test_addr, 4, 1, 1, '02')
        assert str(test_addr) == "1:2"

        test_addr = Address("1:X'0203'")
        self.match_address(test_addr, 4, 1, 2, '0203')
        assert str(test_addr) == "1:0x0203"

        # test bad network
        with self.assertRaises(ValueError):
            Address("65536:X'02'")

    def test_address_global_broadcast(self):
        if _debug: TestAddress._debug("test_address_global_broadcast")

        # test local broadcast
        test_addr = Address("*:*")
        self.match_address(test_addr, 5, None, None, None)
        assert str(test_addr) == "*:*"


@bacpypes_debugging
class TestLocalStation(unittest.TestCase, MatchAddressMixin):

    def test_local_station(self):
        if _debug: TestLocalStation._debug("test_local_station")

        # one parameter
        with self.assertRaises(TypeError):
            LocalStation()

        # test integer
        test_addr = LocalStation(1)
        self.match_address(test_addr, 2, None, 1, '01')
        assert str(test_addr) == "1"

        test_addr = LocalStation(254)
        self.match_address(test_addr, 2, None, 1, 'fe')
        assert str(test_addr) == "254"

        # test bad integer
        with self.assertRaises(ValueError):
            LocalStation(-1)
        with self.assertRaises(ValueError):
            LocalStation(256)

        # test bytes
        test_addr = LocalStation(xtob('01'))
        self.match_address(test_addr, 2, None, 1, '01')
        assert str(test_addr) == "1"

        test_addr = LocalStation(xtob('fe'))
        self.match_address(test_addr, 2, None, 1, 'fe')
        assert str(test_addr) == "254"

        # multi-byte strings are hex encoded
        test_addr = LocalStation(xtob('0102'))
        self.match_address(test_addr, 2, None, 2, '0102')
        assert str(test_addr) == "0x0102"

        test_addr = LocalStation(xtob('010203'))
        self.match_address(test_addr, 2, None, 3, '010203')
        assert str(test_addr) == "0x010203"

        # match with an IPv4 address
        test_addr = LocalStation(xtob('01020304bac0'))
        self.match_address(test_addr, 2, None, 6, '01020304bac0')
        assert str(test_addr) == "1.2.3.4"

@bacpypes_debugging
class TestRemoteStation(unittest.TestCase, MatchAddressMixin):

    def test_remote_station(self):
        if _debug: TestRemoteStation._debug("test_remote_station")

        # two parameters, correct types
        with self.assertRaises(TypeError):
            RemoteStation()
        with self.assertRaises(TypeError):
            RemoteStation(1, 2, 3)
        with self.assertRaises(TypeError):
            RemoteStation('x', 2)

        # test bad network
        with self.assertRaises(ValueError):
            RemoteStation(-1, 1)
        with self.assertRaises(ValueError):
            RemoteStation(65536, 1)

    def test_remote_station_ints(self):
        if _debug: TestRemoteStation._debug("test_remote_station_ints")

        # test integer
        test_addr = RemoteStation(1, 1)
        self.match_address(test_addr, 4, 1, 1, '01')
        assert str(test_addr) == "1:1"

        test_addr = RemoteStation(1, 254)
        self.match_address(test_addr, 4, 1, 1, 'fe')
        assert str(test_addr) == "1:254"

        # test station address
        with self.assertRaises(ValueError):
            RemoteStation(1, -1)
        with self.assertRaises(ValueError):
            RemoteStation(1, 256)

    def test_remote_station_bytes(self):
        if _debug: TestRemoteStation._debug("test_remote_station_bytes")

        # multi-byte strings are hex encoded
        test_addr = RemoteStation(1, xtob('0102'))
        self.match_address(test_addr, 4, 1, 2, '0102')
        assert str(test_addr) == "1:0x0102"

        test_addr = RemoteStation(1, xtob('010203'))
        self.match_address(test_addr, 4, 1, 3, '010203')
        assert str(test_addr) == "1:0x010203"

        # match with an IPv4 address
        test_addr = RemoteStation(1, xtob('01020304bac0'))
        self.match_address(test_addr, 4, 1, 6, '01020304bac0')
        assert str(test_addr) == "1:1.2.3.4"


@bacpypes_debugging
class TestLocalBroadcast(unittest.TestCase, MatchAddressMixin):

    def test_local_broadcast(self):
        if _debug: TestLocalBroadcast._debug("test_local_broadcast")

        # no parameters
        with self.assertRaises(TypeError):
            LocalBroadcast(1)

        test_addr = LocalBroadcast()
        self.match_address(test_addr, 1, None, None, None)
        assert str(test_addr) == "*"


@bacpypes_debugging
class TestRemoteBroadcast(unittest.TestCase, MatchAddressMixin):

    def test_remote_broadcast(self):
        if _debug: TestRemoteBroadcast._debug("test_remote_broadcast")

        # one parameter, correct type
        with self.assertRaises(TypeError):
            RemoteBroadcast()
        with self.assertRaises(TypeError):
            RemoteBroadcast('x')

        # test bad network
        with self.assertRaises(ValueError):
            RemoteBroadcast(-1)
        with self.assertRaises(ValueError):
            RemoteBroadcast(65536)

        # match
        test_addr = RemoteBroadcast(1)
        self.match_address(test_addr, 3, 1, None, None)
        assert str(test_addr) == "1:*"


@bacpypes_debugging
class TestGlobalBroadcast(unittest.TestCase, MatchAddressMixin):

    def test_global_broadcast(self):
        if _debug: TestGlobalBroadcast._debug("test_global_broadcast")

        # no parameters
        with self.assertRaises(TypeError):
            GlobalBroadcast(1)

        test_addr = GlobalBroadcast()
        self.match_address(test_addr, 5, None, None, None)
        assert str(test_addr) == "*:*"


@bacpypes_debugging
class TestAddressEquality(unittest.TestCase, MatchAddressMixin):

    def test_address_equality(self):
        if _debug: TestAddressEquality._debug("test_address_equality")

        assert Address(1) == LocalStation(1)
        assert Address("2") == LocalStation(2)
        assert Address("*") == LocalBroadcast()
        assert Address("3:4") == RemoteStation(3, 4)
        assert Address("5:*") == RemoteBroadcast(5)
        assert Address("*:*") == GlobalBroadcast()
