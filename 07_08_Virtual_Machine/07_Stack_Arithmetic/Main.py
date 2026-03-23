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
from Parser import Parser
from CodeWriter import CodeWriter
from Parser import CommandType



def translate_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Translates a single file.

    Args:
        input_file (typing.TextIO): the file to translate.
        output_file (typing.TextIO): writes all output to this file.
    """
    # Your code goes here!
    # It might be good to start with something like:
    # parser = Parser(input_file)
    # code_writer = CodeWriter(output_file)


    # initialization 
    parsed = Parser(input_file)

    input_filename, input_extension = os.path.splitext(os.path.basename(input_file.name))
    
    code_writer = CodeWriter(output_file)
    code_writer.set_file_name(input_filename)

    while parsed.has_more_commands():
        parsed.advance()
        type_of_command = parsed.command_type()


        # if its not a return command

        if type_of_command == CommandType.C_ARITHMETIC.value:
            arg_1 = parsed.arg1()
            code_writer.write_arithmetic(arg_1)
            continue

        elif type_of_command in [CommandType.C_PUSH.value, CommandType.C_POP.value]:
            arg_1 = parsed.arg1()
            arg_2 = parsed.arg2()
            code_writer.write_push_pop(type_of_command, arg_1, arg_2)
            continue


        # NOTE: WE IGNORE CASE - RELEVANT FOR PROJECT 8
        elif type_of_command == CommandType.C_RETURN.value:
            # todo enploment in project 8
            continue

        elif type_of_command == CommandType.C_FUNCTION.value:
            arg_1 = parsed.arg1()
            arg_2 = parsed.arg2()
            continue
            #todo emploment project 8

        elif type_of_command == CommandType.C_CALL.value:
            arg_1 = parsed.arg1()
            arg_2 = parsed.arg2()
            continue
            #todo emploment project 8



        # TODO: add other commands type checks that are relevant for PROJECT 8













        
        
        


if "__main__" == __name__:
    # Parses the input path and calls translate_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: VMtranslator <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_translate = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
        output_path = os.path.join(argument_path, os.path.basename(
            argument_path))
    else:
        files_to_translate = [argument_path]
        output_path, extension = os.path.splitext(argument_path)
    output_path += ".asm"
    with open(output_path, 'w') as output_file:
        for input_path in files_to_translate:
            filename, extension = os.path.splitext(input_path)
            if extension.lower() != ".vm":
                continue
            with open(input_path, 'r') as input_file:
                translate_file(input_file, output_file)
