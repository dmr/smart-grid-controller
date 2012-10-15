from _utils import sugarjar_path
import unittest

from smart_grid_controller.cli_parser import get_parser


def do_parser_test(
        string,
        ):
    parsed_args = get_parser().parse_args(string.split())
    #print parsed_args

    parsed_args_dct = parsed_args.__dict__

    parsed_args_dct['dry_run'] = True

    kw = parsed_args_dct.pop('execute_function')(
        **parsed_args_dct
    )
    import pprint
    pprint.pprint(kw)

    return kw
do_parser_test.__test__ = False


class ControllerActorServerCliParserTest(unittest.TestCase):
    def test_actor_hostname_port_value(self):
        kw = do_parser_test(
            '-a http://localhost:9000 --sugar-jar {0}'.format(
                sugarjar_path
            )
        )
        assert kw['actor'].__class__.__name__ == "ControllerActor"
        assert len(kw['actor']._actors) == 1, kw['actor']._actors
        assert kw['actor']._actors[0]['uri'] == "http://localhost:9000",\
            kw['actor']._actors[0]['uri']

    def test_actor_hostname_port_value(self):
        kw = do_parser_test(
            '-a http://localhost:9000 http://localhost:9001 --sugar-jar {0}'.format(
                sugarjar_path
            )
        )
        assert kw['actor'].__class__.__name__ == "ControllerActor"
        assert len(kw['actor']._actors) == 2, kw['actor']._actors
