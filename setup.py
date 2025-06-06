# -*- coding: utf-8 -*-
"""Setup file for pip install"""
from pathlib import Path

import setuptools

project_dir = Path(__file__).parent

setuptools.setup(
    name="bach_generator",
    version="1.2.1",
    description="Machine learning based Bach music generator",
    long_description=project_dir.joinpath("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    keywords=["python"],
    author="Richard Baltrusch",
    url="https://github.com/rbaltrusch/bach_generator",
    packages=setuptools.find_packages("."),
    python_requires=">=3.8",
    include_package_data=True,
    package_data={"bach_generator": ["py.typed"]},  # for mypy
    # This is a trick to avoid duplicating dependencies between both setup.py and requirements.txt.
    # requirements.txt must be included in MANIFEST.in for this to work.
    install_requires=project_dir.joinpath("requirements.txt")
    .read_text(encoding="utf-8")
    .split("\n"),
    zip_safe=False,
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        # 3.12 doesn't work with setup.py, see: https://stackoverflow.com/questions/73533994/sub-package-not-importable-after-installation  pylint: disable=line-too-long
        # "Programming Language :: Python :: 3.12",
        "Topic :: Artistic Software",
        "Topic :: Desktop Environment",
        "Topic :: Multimedia",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Multimedia :: Sound/Audio :: MIDI",
        "Topic :: Multimedia :: Sound/Audio :: Sound Synthesis",
        "Topic :: Scientific/Engineering",
        "Typing :: Typed",
    ],
)
