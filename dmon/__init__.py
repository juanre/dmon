# -*- coding: utf-8 -*-
"""Manipulate monetary values with control of the date when conversions happen.
"""


def main():
    import argparse
    import dmon.money

    parser = argparse.ArgumentParser(description=__doc__)
    dmon.money.add_args(parser)

    dmon.money.main(parser.parse_args())
