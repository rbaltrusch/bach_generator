[![Unit tests](https://github.com/rbaltrusch/bach_generator/actions/workflows/pytest-unit-tests.yml/badge.svg)](https://github.com/rbaltrusch/bach_generator/actions/workflows/pytest-unit-tests.yml)
[![Pylint](https://github.com/rbaltrusch/bach_generator/actions/workflows/pylint.yml/badge.svg)](https://github.com/rbaltrusch/bach_generator/actions/workflows/pylint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](https://opensource.org/licenses/MIT)

# Bach music generator

A Bach music generator using a neural network trained with a genetic algorithm.

## Motivation

The neural network was setup and trained from scratch. The main motivation behind this was learning how one might code a neural network without using a library abstracting away all the details.
It's obviously not very efficient, because it is not optimized for speed and doesn't use the GPU (so if you want to run this, I hope you have a fast CPU), but this doesn't matter, as speed is not within the scope of this experiment.

## Getting started

Install the package using pip, then run it with no arguments to open the graphical user interface:

```
python -m pip install bach_generator
python -m bach_generator
```

Bypass the graphical user interface by calling the package and passing a midi filepath to it:

```
python -m bach_generator <midi_filepath>
```

For more CLI options, please see the [CLI documentation](https://github.com/rbaltrusch/bach_generator/blob/master/README#command-line-interface) or run the help command:

```
python -m bach_generator -h
```

## Algorithm

At the start, several separate neural networks are instantiated and fed the input data. The top ranked models (based on the correlation of their output to the input) get cloned into the next generation with randomly adjusted weights. This process is repeated over a number of generations.

Currently, the neural network iterates through all notes in a given midi file, feeding the neural network the current note and a calibratable number of past notes. Each node in the model is
connected to all nodes from the previous network. When inputs are fed in to the model, they arrive at the input layer, get multiplied by the weights of the input nodes, then get propagated to
the next layer. Each node in the middle layers averages all values it receives, then weights that value and propagates it further.

This mixture of past and present inputs makes this stateless model behave as if it was stateful, e.g. like a recurrent neural network (RNN).

Finally, the output values are received, decoded from numbers into notes and written to an output midi file.

Currently the node decoding happens using a simple frequency ranking analogue to the input note frequency. The rhythms in the input midi file are retained in the output.

## Training data

Training data was downloaded from [www.jsbach.net](http://www.jsbach.net/midi/) and is not included in this repository.

A pre-trained object model (reaching 78% correlation for the entire Goldberg variations BWV 988, with over 90% correlation for some variations) can be found [here](https://github.com/rbaltrusch/bach_generator/blob/master/models/models.json). Load and run further simulations with it by using the CLI `--load` flag:

```
python -m bach_generator --load=models/models.json --layer-type=object <midi_filepath>
```

## Command line interface

The Bach generator package supports a number of command line interface arguments, including handling output, model save/load, and parameters regarding model size and cloning.

A brief overview of the CLI is shown below:

```
usage: __main__.py [-h] [--generations GENERATIONS] [--save]
                   [--load LOAD_FILEPATH] [--load-best LOAD_BEST]
                   [--models MODELS] [--inputs INPUTS] [--layers LAYERS]
                   [--layer-size LAYER_SIZE] [--select-models SELECT_MODELS]
                   [--clones CLONES] [--weight-jumble-by {offset,selection}]
                   [--weight-divergence WEIGHT_DIVERGENCE]
                   [--write-interval WRITE_INTERVAL] [--output-dir OUTPUT_DIR]
                   [--seed SEED]
                   filepath

positional arguments:
  filepath              The filepath to the midi file to be analysed

optional arguments:
  -h, --help            show this help message and exit
```

To see the full CLI documentation, run the CLI help command:

```
python -m bach_generator -h
```

Running the package without specifying any CLI arguments with `python -m bach_generator` instead opens the graphical user interface:

![Screenshot of the analysis GUI](https://github.com/rbaltrusch/bach_generator/blob/master/bach_generator/gui/media/screenshot.PNG?raw=true "Screenshot of the analysis GUI")

## Contributions

To contribute, please read the [contribution guidelines](https://github.com/rbaltrusch/bach_generator/blob/master/CONTRIBUTING.md).

## Python

Written in Python 3.8.8.

## License

This repository is open-source software available under the [MIT License](https://github.com/rbaltrusch/bach_generator/blob/master/LICENSE).

## Contact

Please raise an issue for code changes. To reach out, please send an email to richard@baltrusch.net.
