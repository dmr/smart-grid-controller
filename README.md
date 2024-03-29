Smart-Grid-Controller
---------------------

An implementation for a Smart Grid Controller Actor.
The package provides a CLI "smart_grid_controller" to start a Smart Grid Controller Actor Server.


Installation
------------

Just use pip to install

    pip install git+http://github.com/dmr/smart-grid-controller.git#egg=smart_grid_controller

This will install all dependencies needed, including http://github.com/dmr/csp-solver and http://github.com/dmr/smart-grid-actor.

Additionally, you will need to have minisat2 installed in $PATH. See http://github.com/dmr/csp-solver for a more detailed installation description.



Tests
-----

To run the tests, install spec and/or nose and requests and run them:

    pip install spec requests
    nosetests

Thank you http://travis-ci.org for running the tests :)
[![Build Status](https://travis-ci.org/dmr/smart-grid-controller.png)](https://travis-ci.org/dmr/smart-grid-controller)
