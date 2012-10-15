#!/usr/bin/env python
from smart_grid_controller.cli_parser import get_parser

def main():
    parser = get_parser()
    parsed_args_dct = parser.parse_args().__dict__
    parsed_args_dct.pop('execute_function')(**parsed_args_dct)
