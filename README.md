# Homework 1

## Description

This project demonstrates the usage of `main.py`, `Makefile`, and `PartitionTypes.csv` to perform MBR GPT Analysis.

## Usage

1. run `make` to generate `boot_info` and hashes of the sample files.
2. Run the command with the format `./boot_info -f filename.raw -o number1 number2 number3`
3. Example Usage: `./boot_info -f ./samples/gpt_sample.raw -o 323 532 123`

## Makefile

The `Makefile` provides a convenient way to build and run the project. Here are some useful commands:

- `make`: Compiles any necessary files or dependencies.
- `make clean`: Removes _boot_info_.
