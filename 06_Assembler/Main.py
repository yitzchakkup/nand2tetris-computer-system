"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from SymbolTable import SymbolTable
from Parser import A_INSTRUCTION, C_INSTRUCTION, L_INSTRUCTION, Parser
from Code import Code


def assemble_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Assembles a single file.

    Args:
        input_file (typing.TextIO): the file to assemble.
        output_file (typing.TextIO): writes all output to this file.
    """
    # Your code goes here!
    # A good place to start is to initialize a new Parser object:
    # parser = Parser(input_file)
    # Note that you can write to output_file like so:
    # output_file.write("Hello world! \n")
    num_command = 0
    my_parser = Parser(input_file)
    my_symole_table = SymbolTable()
    # first iteration 
    while my_parser.has_more_commands():
        my_parser.advance()
        if my_parser.command_type() == L_INSTRUCTION:
            if not (my_symole_table.contains(my_parser.symbol())):  # reference is new
                my_symole_table.add_entry(my_parser.symbol(), num_command)
        else:
            num_command += 1

    # Second iteration
    input_file.seek(0)
    new_parser = Parser(input_file)
    symbol_num = 16  # from here we'll save symbols
    while new_parser.has_more_commands():
        new_parser.advance()
        if new_parser.command_type() == A_INSTRUCTION:  # A command
            if new_parser.symbol().isdigit():  # meaning its @num (actual number, not a symbol)
                binary_form = format(int(new_parser.symbol()), '016b')
                output_file.write(binary_form + "\n")
                continue
            if not my_symole_table.contains(new_parser.symbol()):
                my_symole_table.add_entry(new_parser.symbol(), symbol_num)
                symbol_num += 1
            binary_form = format(my_symole_table.get_address(new_parser.symbol()), '016b')
            output_file.write(binary_form + "\n")
            continue
        #if new_parser.command_type() == L_INSTRUCTION:
        #    binary_form = format(my_symole_table.get_address(new_parser.symbol()), '016b')
        #    output_file.write(str(binary_form)+ "\n")

        # C command:
        if new_parser.command_type() == C_INSTRUCTION:
            dest = new_parser.dest()
            comp = new_parser.comp()
            jump = new_parser.jump()
            output_file.write(str(Code.comp(comp)) + str(Code.dest(dest)) + str(Code.jump(jump)) + "\n")


if "__main__" == __name__:
    # Parses the input path and calls assemble_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: Assembler <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".asm":
            continue
        output_path = filename + ".hack"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            assemble_file(input_file, output_file)
