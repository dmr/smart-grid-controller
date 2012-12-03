from __future__ import print_function

import sys
import argparse
import urlparse

from smart_grid_actor.server import start_actor_server
from smart_grid_actor.cli_parser import add_actor_base_parser_params

from smart_grid_controller.remote_actor import RemoteActor
from smart_grid_controller.controller import ControllerActor

csp_not_installed_msg = (
    "csp_solver not installed! "
    "To start Controller Actors install csp_solver from "
    "http://github.com/dmr/csp-solver.git")
try:
    import csp_solver
except ImportError:
    print("Warning:", csp_not_installed_msg)
    raise


def check_uri(uri):
    parsed = urlparse.urlparse(uri)
    if not parsed.scheme in ["http", "https"]:
        raise argparse.ArgumentTypeError(
            "%r is not a valid URL. scheme must be http(s)!" % uri)

    # cut off fragment
    uri = urlparse.urlunparse((parsed.scheme, parsed.netloc, parsed.path,
                               parsed.params, parsed.query, ""))
    return uri


def get_parser():
    parser = argparse.ArgumentParser(
        "smart_grid_controller",
        description=(
            "Start a Smart Grid Controller Actor server."
            )
    )
    add_actor_base_parser_params(parser)
    add_controller_actor_params(parser)
    return parser


def start_controller_actor(
        host_name,
        port,
        minisat,
        sugar_jar,
        tmp_folder,
        actor_uris,
        log_requests,
        check_actor_uris,
        worker_count=None,
        dry_run=False,
        ):

    csp_solver_config = csp_solver.get_valid_csp_solver_config(
        minisat_path=minisat,
        sugarjar_path=sugar_jar,
        tmp_folder=tmp_folder
    )

    actors=[RemoteActor(actor_uri)
            for actor_uri in actor_uris]

    pool_kwargs = {}
    if worker_count:
        pool_kwargs['processes'] = worker_count

    import multiprocessing
    pool = multiprocessing.Pool(**pool_kwargs)

    actor = ControllerActor(
        actors=actors,
        csp_solver_config=csp_solver_config,
        multiprocessing_pool=pool
    )

    if check_actor_uris:
        # test is actors of a ControllerActor exist
        # to prevent errors later
        for actor in actor._actors:
            import urllib2
            try:
                actor.get_value()
            except urllib2.URLError as exc:
                print("Error while checking {0}: {1}".format(actor, exc.reason))
                import sys
                sys.exit(1)

    kw = dict(
        host_port_tuple=(host_name, port),
        actor=actor
    )
    if dry_run:
        print("Would start an actor controller on {0} "
            "but this is a test run".format(kw))
        return kw

    try:
        start_actor_server(**kw)
    except KeyboardInterrupt:
        pool.terminate()
    except Exception, e:
        pool.terminate()
    finally:
        pool.join()


def add_controller_actor_params(parser):
    parser.add_argument('-a', '--actor-uris', nargs='+',
        type=check_uri, required=True,
        help="URIs for remote actors of this controller actor actor"
    )

    parser.add_argument('--check-actor-uris',
        action="store_true", default=False,
        help="Check if the actor URIs can be queried before starting the ControllerActor server. default: False"
    )

    parser.add_argument('--worker-count',
        help=(
            "Worker count for the parallel processing module. "
            "Defaults to CPU cores count"
            )
    )

    # The following arguments are not pretty here. They belong to
    # the CSP configuration but are needed if an actor_controller
    # is started
    # Easy defaults: current folder. Will fail if files don't exist
    parser = csp_solver.add_csp_config_params_to_argparse_parser(parser)

    parser.set_defaults(
        execute_function=start_controller_actor
    )
