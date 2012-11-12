#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import time

from smart_grid_actor.actor import Actor, NotSolvable
from smart_grid_actor.server import start_actor_server
from smart_grid_actor.test._utils import AbstractInterface

from smart_grid_controller.test._utils import csp_solver_config
from smart_grid_controller.controller import (
    RemoteActor,
    ControllerActor
)


class ControllerOfControllerActorInterface(unittest.TestCase):
    def setUp(self):
        self.a1 = Actor([5, 6])
        self.a2 = Actor([7, 8])
        self.a3 = ControllerActor(
            actors=[self.a1, self.a2],
            csp_solver_config=csp_solver_config,
        )

        self.a4 = Actor([-5, -6])
        self.a5 = Actor([-7, -8])
        self.a6 = ControllerActor(
            actors=[self.a4, self.a5],
            csp_solver_config=csp_solver_config,
        )

    def test_set_value_failure_str(self):
        a7 = ControllerActor(
            actors=[self.a3, self.a6],
            csp_solver_config=csp_solver_config,
        )

        a7_vr = a7.get_value_range()
        assert a7_vr == [-2, -1, 0, 1, 2], a7_vr

    def test_set_value_failure_str(self):
        a7 = ControllerActor(
            actors=[self.a3, self.a6],
            csp_solver_config=csp_solver_config,
        )

        a7.set_value(0)

        a7_value = a7.get_value()
        assert a7_value == 0, a7_value


class RemoteActorInterfaceControllingControllerActorOfActor(
        AbstractInterface, unittest.TestCase
        ):
    def setUp(self):
        uri, self._actor_server_process = start_actor_server(
            start_in_background_thread=True,
            actor=ControllerActor(
                actors=[
                    Actor(value_range=[1,2,3])
                ],
                csp_solver_config=csp_solver_config,
            )
        )
        self.a1 = RemoteActor(uri=uri)
        time.sleep(.8)

    def tearDown(self):
        self._actor_server_process.terminate()
        self._actor_server_process.join()


class RemoteActorInterfaceControllingControllerActorOfRemoteActor(
    AbstractInterface, unittest.TestCase
):
    def setUp(self):
        uri1, self._actor_server_process_1 = start_actor_server(
            start_in_background_thread=True,
            actor=Actor(value_range=[1,2,3])
        )
        uri2, self._actor_server_process_2 = start_actor_server(
            start_in_background_thread=True,
            actor=ControllerActor(
                actors=[
                    RemoteActor(uri=uri1)
                ],
                csp_solver_config=csp_solver_config,
            )
        )
        self.a1 = RemoteActor(uri=uri2)
        time.sleep(.8)

    def tearDown(self):
        self._actor_server_process_1.terminate()
        self._actor_server_process_1.join()
        self._actor_server_process_2.terminate()
        self._actor_server_process_2.join()


ControllerOfControllerActorInterface.__test__ = False
RemoteActorInterfaceControllingControllerActorOfActor.__test__ = False
RemoteActorInterfaceControllingControllerActorOfRemoteActor.__test__ = False
