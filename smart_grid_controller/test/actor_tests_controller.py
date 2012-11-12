#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

from smart_grid_actor.actor import Actor, NotSolvable

from smart_grid_controller.test._utils import csp_solver_config
from smart_grid_controller.controller import (
    ControllerActor
)


class ControllerActorInterface(unittest.TestCase):
    def setUp(self):
        self.a1 = Actor([1, 3])
        self.a2 = Actor(range(-10, -7+1))
        super(ControllerActorInterface, self).setUp()

    def test_init_raises_exception_not_an_actor(self):
        self.failUnlessRaises(
            Exception, # TODO raise own exception
            ControllerActor,
            actors=[self.a1, self.a2, '3'],
            csp_solver_config=csp_solver_config,
        )

    def test_init(self):
        a3 = ControllerActor(
            actors=[self.a1, self.a2],
            csp_solver_config=csp_solver_config,
        )
        assert a3.id

    def test_get_value(self):
        a3 = ControllerActor(
            actors=[self.a1, self.a2],
            csp_solver_config=csp_solver_config,
        )

        assert self.a1.get_value() == 1, self.a1.get_value()
        assert self.a2.get_value() == -10, self.a2.get_value()

        a3_value = a3.get_value()
        assert type(a3_value) == int
        assert a3_value == -9

    def test_get_value_range(self):
        a3 = ControllerActor(
            actors=[self.a1, self.a2],
            csp_solver_config=csp_solver_config,
        )
        a3_value_range = a3.get_value_range()
        assert a3_value_range == set([-9, -8, -7, -6, -5, -4]), \
            a3_value_range

    def test_set_value_int(self):
        a3 = ControllerActor(
            actors=[self.a1, self.a2],
            csp_solver_config=csp_solver_config,
        )
        assert self.a1.get_value() == 1, self.a1.get_value()
        assert self.a2.get_value() == -10, self.a2.get_value()
        assert a3.get_value() == -9, a3.get_value()

        ret_val = a3.set_value(-4)

        assert ret_val == -4

        assert self.a1.get_value() == 3, self.a1.get_value()
        assert self.a2.get_value() == -7, self.a2.get_value()
        assert a3.get_value() == -4, a3.get_value()

    def test_set_value_int_out_of_range(self):
        a3 = ControllerActor(
            actors=[self.a1, self.a2],
            csp_solver_config=csp_solver_config,
        )
        self.failUnlessRaises(
            NotSolvable,
            a3.set_value,
            0
        )

    def test_set_value_float(self):
        a3 = ControllerActor(
            actors=[self.a1, self.a2],
            csp_solver_config=csp_solver_config,
        )
        assert self.a1.get_value() == 1, self.a1.get_value()
        assert self.a2.get_value() == -10, self.a2.get_value()
        assert a3.get_value() == -9, a3.get_value()

        ret_val = a3.set_value(-4.5)

        self.assertEqual(ret_val, -4)

        self.assertEqual(
            a3.get_value(), -4
        )

        self.assertEqual(
            self.a1.get_value(), 3
        )
        self.assertEqual(
            self.a1.get_value(), 3
        )

    def test_set_value_string(self):
        a3 = ControllerActor(
            actors=[self.a1, self.a2],
            csp_solver_config=csp_solver_config,
        )
        assert self.a1.get_value() == 1, self.a1.get_value()
        assert self.a2.get_value() == -10, self.a2.get_value()
        assert a3.get_value() == -9, a3.get_value()

        a3.set_value("-4")

        assert self.a1.get_value() == 3, self.a1.get_value()
        assert self.a2.get_value() == -7, self.a2.get_value()
        assert a3.get_value() == -4, a3.get_value()
        assert type(a3.get_value()) == int

    def test_set_value_string_invalid(self):
        a3 = ControllerActor(
            actors=[self.a1, self.a2],
            csp_solver_config=csp_solver_config,
        )
        self.failUnlessRaises(
            NotSolvable,
            a3.set_value,
            "null"
        )
