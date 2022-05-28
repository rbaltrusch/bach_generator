# -*- coding: utf-8 -*-
"""Tests for the cli module"""

import pytest
from bach_generator import cli


def test_no_filepath():
    parser = cli.construct_parser()
    with pytest.raises(SystemExit):
        parser.parse_args("")


@pytest.mark.parametrize(
    "input_args, expected", [("a", "a"), ("test_dir/test.midi", "test_dir/test.midi")]
)
def test_filepath(input_args, expected):
    parser = cli.construct_parser()
    args = parser.parse_args(input_args.split())
    assert args.filepath == expected


@pytest.mark.parametrize(
    "input_args, expected",
    [
        ("a --generations 12", 12),
        ("a -g 3", 3),
    ],
)
def test_generations(input_args, expected):
    parser = cli.construct_parser()
    args = parser.parse_args(input_args.split())
    assert args.generations == expected


@pytest.mark.parametrize(
    "input_args, expected",
    [
        ("a", False),
        ("a --save", True),
    ],
)
def test_save(input_args, expected):
    parser = cli.construct_parser()
    args = parser.parse_args(input_args.split())
    assert args.save == expected


@pytest.mark.parametrize(
    "input_args, expected",
    [
        ("a", None),
        ("a --load test.json", "test.json"),
    ],
)
def test_load(input_args, expected):
    parser = cli.construct_parser()
    args = parser.parse_args(input_args.split())
    assert args.load_filepath == expected


@pytest.mark.parametrize(
    "input_args, expected",
    [
        ("a", None),
        ("a --load-best 23", 23),
    ],
)
def test_load_best(input_args, expected):
    parser = cli.construct_parser()
    args = parser.parse_args(input_args.split())
    assert args.load_best == expected


@pytest.mark.parametrize(
    "input_args, expected",
    [
        ("a --models 234", 234),
        ("a -m 4", 4),
    ],
)
def test_models(input_args, expected):
    parser = cli.construct_parser()
    args = parser.parse_args(input_args.split())
    assert args.models == expected


@pytest.mark.parametrize(
    "input_args, expected",
    [
        ("a --inputs 234", 234),
        ("a -i 45", 45),
    ],
)
def test_inputs(input_args, expected):
    parser = cli.construct_parser()
    args = parser.parse_args(input_args.split())
    assert args.inputs == expected


@pytest.mark.parametrize(
    "input_args, expected",
    [
        ("a --layers 2", 2),
        ("a -l 56", 56),
    ],
)
def test_layers(input_args, expected):
    parser = cli.construct_parser()
    args = parser.parse_args(input_args.split())
    assert args.layers == expected


@pytest.mark.parametrize(
    "input_args, expected",
    [
        ("a --layer-size 23", 23),
        ("a -ls 56", 56),
    ],
)
def test_layer_size(input_args, expected):
    parser = cli.construct_parser()
    args = parser.parse_args(input_args.split())
    assert args.layer_size == expected


@pytest.mark.parametrize(
    "input_args, expected",
    [
        ("a --select-models 26", 26),
        ("a -s 56", 56),
    ],
)
def test_select_models(input_args, expected):
    parser = cli.construct_parser()
    args = parser.parse_args(input_args.split())
    assert args.select_models == expected


@pytest.mark.parametrize(
    "input_args, expected",
    [
        ("a --clones 8", 8),
        ("a -c 98", 98),
    ],
)
def test_clones(input_args, expected):
    parser = cli.construct_parser()
    args = parser.parse_args(input_args.split())
    assert args.clones == expected


@pytest.mark.parametrize(
    "input_args, expected",
    [
        ("a --weight-jumble-by=factor", "factor"),
        ("a -wj=selection", "selection"),
    ],
)
def test_weight_jumble_strategy(input_args, expected):
    parser = cli.construct_parser()
    args = parser.parse_args(input_args.split())
    assert args.weight_jumble_strategy == expected


@pytest.mark.parametrize(
    "input_args",
    [
        "a --weight-jumble-by=factor3",
        "a -wj",
    ],
)
def test_weight_jumble_strategy_fail(input_args):
    parser = cli.construct_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(input_args.split())


@pytest.mark.parametrize(
    "input_args, expected",
    [
        ("a --weight-divergence 0.1", 0.1),
        ("a -wd=-0.5", -0.5),
    ],
)
def test_weight_divergence(input_args, expected):
    parser = cli.construct_parser()
    args = parser.parse_args(input_args.split())
    assert args.weight_divergence == expected


@pytest.mark.parametrize(
    "input_args, expected",
    [
        ("a --write-interval 4", 4),
        ("a -wi 23", 23),
    ],
)
def test_write_interval(input_args, expected):
    parser = cli.construct_parser()
    args = parser.parse_args(input_args.split())
    assert args.write_interval == expected


@pytest.mark.parametrize(
    "input_args, expected",
    [
        ("a --output-dir abc", "abc"),
        ("a -o b", "b"),
    ],
)
def test_output_dir(input_args, expected):
    parser = cli.construct_parser()
    args = parser.parse_args(input_args.split())
    assert args.output_dir == expected


@pytest.mark.parametrize(
    "input_args, expected",
    [
        ("a --rhythm simple", "simple"),
        ("a -r copy", "copy"),
    ],
)
def test_rhythm(input_args, expected):
    parser = cli.construct_parser()
    args = parser.parse_args(input_args.split())
    assert args.rhythm_handler == expected


@pytest.mark.parametrize(
    "input_args",
    [
        "a --rhythm ere",
        "a -r",
    ],
)
def test_rhythm_fail(input_args):
    parser = cli.construct_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(input_args.split())


@pytest.mark.parametrize(
    "input_args, expected",
    [
        ("a", None),
        ("a --seed 2", 2),
    ],
)
def test_seed(input_args, expected):
    parser = cli.construct_parser()
    args = parser.parse_args(input_args.split())
    assert args.seed == expected


def test_display_args():
    "display args smoke test"
    parser = cli.construct_parser()
    args = parser.parse_args(["a"])
    cli.display_args(args)
