# -*- coding: utf-8 -*-
"""Constructs the cli argparser"""

import argparse
import logging


def construct_parser() -> argparse.ArgumentParser:
    """Constructs the cli parser"""

    parser = argparse.ArgumentParser()

    parser.add_argument("filepath", help="The filepath to the midi file to be analysed")

    parser.add_argument(
        "--generations",
        "-g",
        type=int,
        default=10,
        help="The amount of generations for which the experiment should run",
    )

    parser.add_argument(
        "--models",
        "-m",
        type=int,
        default=100,
        help="The amount of models to start the experiment with",
    )

    parser.add_argument(
        "--inputs",
        "-i",
        type=int,
        default=10,
        help="The amount of input notes processed by a neural network model",
    )

    parser.add_argument(
        "--layers",
        "-l",
        type=int,
        default=2,
        help="The amount of hidden layers in the neural network",
    )

    parser.add_argument(
        "--layer-size",
        "-ls",
        type=int,
        default=20,
        help="The amount of nodes in each layer",
    )

    parser.add_argument(
        "--select-models",
        "-s",
        type=int,
        default=20,
        help="The amount of top models to select to survive to the next generation",
    )

    parser.add_argument(
        "--clones",
        "-c",
        type=int,
        default=5,
        help="The amount of clones per selected top models per generation",
    )

    parser.add_argument(
        "--weight-divergence",
        "-wd",
        type=float,
        default=0.05,
        help="The random divergence of neural network weights when cloning",
    )

    parser.add_argument(
        "--write-interval",
        "-wi",
        type=int,
        default=10,
        help="The generation interval between writing top model results to file",
    )

    parser.add_argument(
        "--output-dir",
        "-o",
        default="outputs",
        help="The directory to which generated music will be written to",
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="The random seed to be used for the simulation",
    )

    return parser


def display_args(args):
    """Logs all attributes of the arguments namespace passed"""
    for name, value in vars(args).items():
        logging.info("Using setting %s: %s", name, value)
