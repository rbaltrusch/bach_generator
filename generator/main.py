# -*- coding: utf-8 -*-
"""
Created on Tue Sep 14 17:00:02 2021

@author: Korean_Crimson
"""

import os
import shutil
import datetime
from src.manager import Manager
    
def main():
    input_file = '../data/988-v01.mid'
    date = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    output_directory = f'../outputs/{date}'
    if not os.path.isdir(output_directory):
        os.makedirs(output_directory)
    shutil.copyfile(input_file, os.path.join(output_directory, os.path.basename(input_file)))
    shutil.copyfile('main.py', os.path.join(output_directory, 'main.py'))

    manager = Manager()
    manager.parse(input_file)

    #set up initial 200 models
    managers = []
    for _ in range(200):
        new_manager = Manager()
        new_manager.copy_data_from(manager)
        new_manager.setup_model(inputs=3, outputs=1, layers=2, size=6)
        managers.append(new_manager)

    #genetic algorithm training loop
    for i in range(51):
        for manager in managers:
            manager.run_model()

        managers = sorted(managers, key=lambda x: x.rating, reverse=True)[:40]
        clones = [manager.clone(weight_divergence=0.05) for _ in range(5) for manager in managers]
        managers.extend(clones)
        print(i, managers[0].rating)

        #best manager write output every 10 loops
        if i % 10 == 0:
            best_manager = managers[0]
            rounded_rating = int(round(best_manager.rating, 2) * 100)
            filename = f'output_{i}_{rounded_rating}.mid'
            best_manager.write_output_score(filename, output_directory)

if __name__ == '__main__':
    main()
