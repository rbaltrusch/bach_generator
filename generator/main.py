# -*- coding: utf-8 -*-
"""
Created on Tue Sep 14 17:00:02 2021

@author: Korean_Crimson
"""
import time

from src.encoder import Encoder, Quantizer
from src.judge import Judge
from src.manager import ModelManager
from src.music_handler import CopyMusicHandler
from src.output_handler import OutputHandler


# pylint: disable=too-many-locals
def main():
    """Main function"""
    input_file = "../data/988-v02.mid"
    judge = Judge()

    output_handler = OutputHandler()
    output_handler.setup_output_directory("../outputs")
    output_handler.copy_files(input_file, "main.py")

    music_handler = CopyMusicHandler()
    note_names = music_handler.parse(input_file)

    encoder = Encoder()
    encoded_inputs = encoder.encode(note_names)

    quantizer = Quantizer()
    quantizer.setup(encoded_inputs)

    managers = [
        ModelManager(inputs=10, outputs=1, layers=3, layer_size=20) for _ in range(100)
    ]

    # genetic algorithm training loop
    for i in range(501):
        start_time = time.time()

        for manager in managers:
            manager.run_model(encoded_inputs, quantizer)
            manager.get_rated_by(judge, encoded_inputs)

        managers = sorted(managers, key=lambda x: x.rating, reverse=True)[:20]
        clones = [
            manager.clone(weight_divergence=0.5)
            for _ in range(5)
            for manager in managers
        ]
        managers.extend(clones)

        print(i, managers[0].rating, time.time() - start_time)

        # best manager write output every 10 loops
        if i % 10 == 0:
            best_manager = managers[0]
            rounded_rating = int(round(best_manager.rating, 2) * 100)
            best_manager.decode_outputs(encoder)
            score = music_handler.generate_score(best_manager.decoded_outputs)
            output_handler.write(score, f"output_{i}_{rounded_rating}.mid")


if __name__ == "__main__":
    main()
