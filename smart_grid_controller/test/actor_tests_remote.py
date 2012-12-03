#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import unittest
import urlparse

from smart_grid_actor.actor import Actor
from smart_grid_actor.server import start_actor_server
from smart_grid_actor.test._utils import AbstractInterface

from smart_grid_controller.remote_actor import RemoteActor


class UrlParseLearnTest(unittest.TestCase):
    def test_urljoin(self):
        self.assertEqual(
            'http://test/',
            str(urlparse.urljoin('http://test/', '/'))
        )
        self.assertEqual(
            urlparse.urljoin('http://test', '/'),
            urlparse.urljoin('http://test/', '/'),
        )
        self.assertEqual(
            'http://test/vr/',
            str(urlparse.urljoin('http://test/', '/vr/'))
        )
        self.assertEqual(
            urlparse.urljoin('http://test', '/vr/'),
            urlparse.urljoin('http://test/', '/vr/'),
        )


class RemoteActorInterface(
        AbstractInterface, unittest.TestCase
        ):
    def setUp(self):
        uri, self._actor_server_process = start_actor_server(
            start_in_background_thread=True,
            actor=Actor(value_range=[1,2,3])
        )
        self.a1 = RemoteActor(uri=uri)
        time.sleep(.8)

    def tearDown(self):
        self._actor_server_process.terminate()
        self._actor_server_process.join()


class RemoteActorInterfaceUrlTest(
        AbstractInterface, unittest.TestCase
        ):
    def setUp(self):
        uri, self._actor_server_process = start_actor_server(
            start_in_background_thread=True,
            actor=Actor(value_range=[1,2,3])
        )
        # url ends with a '/'! --> test how /vr/ url is created
        self.a1 = RemoteActor(uri=uri)
        time.sleep(.8)

    def tearDown(self):
        self._actor_server_process.terminate()
        self._actor_server_process.join()
