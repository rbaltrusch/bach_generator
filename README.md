[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](https://opensource.org/licenses/MIT)

# Bach music generator

A Bach music generator using a neural network trained using a genetic algorithm.

## Motivation

The neural network was setup and trained from scratch. The main motivation behind this was learning how one might code a neural network without using a library abstracting away all the details.
It's obviously not very efficient, because it is not optimized for speed and doesn't use the GPU (so if you want to run this, I hope you have a fast CPU), but this doesn't matter,
as speed is not within the scope of this experiment.

## Status quo

I want machine learning!

We have machine learning at home...

Machine learning at home: this

## Algorithm

At the start, 200 separate neural networks are instantiated and fed the input data. The top ranked models (based on the correlation of their output to the input) get cloned into the next generation with randomly adjusted weights. This process is repeated over a number of generations.

Currently, the neural network iterates through all notes in a given midi file, feeding the neural network the current note and a calibratable number of past notes. Each node in the model is
connected to all nodes from the previous network. When inputs are fed in to the model, they arrive at the input layer, get multiplied by the weights of the input nodes, then get propagated to
the next layer. Each node in the middle layers averages all values it receives, then weights that value and propagates it further.

This mixture of past and present inputs makes this stateless model behave as if it was stateful, e.g. like a recurrent neural network (RNN).

Finally, the output values are received, decoded from numbers into notes and written to an output midi file.

Currently the node decoding happens using a simple frequency ranking analogue to the input note frequency. The rhythms in the input midi file are retained in the output.

## Getting started

To get a copy of this repository, simply open up git bash in an empty folder and use the command:

    $ git clone https://github.com/rbaltrusch/bach_generator

To install all python dependencies, run the following in your command line:

    python -m pip install -r requirements.txt

## Contributions

To contribute, please read the [contribution guidelines](CONTRIBUTING.md).

## Python

Written in Python 3.8.8.

## License

This repository is open-source software available under the [MIT License](https://github.com/rbaltrusch/bach_generator/blob/master/LICENSE).

## Contact

Please raise an issue for code changes. To reach out, please send an email to richard@baltrusch.net.
