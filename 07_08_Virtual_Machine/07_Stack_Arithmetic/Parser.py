"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from enum import Enum


class CommandType(Enum):
    C_ARITHMETIC = "C_ARITHMETIC"
    C_PUSH = "C_PUSH"
    C_POP = "C_POP"
    C_LABEL = "C_LABEL"
    C_GOTO = "C_GOTO"
    C_IF = "C_IF"
    C_FUNCTION = "C_FUNCTION"
    C_RETURN = "C_RETURN"
    C_CALL = "C_CALL"


VM_COMMANDS_TO_TYPE_MAP = {
    "add": "C_ARITHMETIC",
    "sub": "C_ARITHMETIC",
    "neg": "C_ARITHMETIC",
    "eq": "C_ARITHMETIC",
    "gt": "C_ARITHMETIC",
    "lt": "C_ARITHMETIC",
    "and": "C_ARITHMETIC",
    "or": "C_ARITHMETIC",
    "not": "C_ARITHMETIC",
    "push": "C_PUSH",
    "pop": "C_POP",
    "label": "C_LABEL",
    "goto": "C_GOTO",
    "if-goto": "C_IF",
    "function": "C_FUNCTION",
    "return": "C_RETURN",
    "call": "C_CALL"
}


class Parser:
    """
    # Parser
    
    Handles the parsing of a single .vm file, and encapsulates access to the
    input code. It reads VM commands, parses them, and provides convenient 
    access to their components. 
    In addition, it removes all white space and comments.
    
    ## VM Language Specification

    A .vm file is a stream of characters. If the file represents a
    valid program, it can be translated into a stream of valid assembly 
    commands. VM commands may be separated by an arbitrary number of whitespace
    characters and comments, which are ignored. Comments begin with "//" and
    last until the line’s end.
    The different parts of each VM command may also be separated by an arbitrary
    number of non-newline whitespace characters.

    - Arithmetic commands:
        - add, sub, and, or, eq, gt, lt
        - neg, not, shiftleft, shiftright
    - Memory segment manipulation:
        - push <segment> <number>
        - pop <segment that is not constant> <number>
        - <segment> can be any of: argument, local, static, constant, this, that, 
                                                                pointer, temp
    - Branching (only relevant for project 8):
        - label <label-name>
        - if-goto <label-name>
        - goto <label-name>
        - <label-name> can be any combination of non-whitespace characters.
    - Functions (only relevant for project 8):
        - call <function-name> <n-args>
        - function <function-name> <n-vars>
        - return
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Gets ready to parse the input file.

        Args:
                input_file (typing.TextIO): input file.
        """
        
        # we can assue the file represent a valid file.vm program
        input_lines = input_file.read().splitlines()
        cleaned_lines = []
        for line in input_lines:
            # Remove comments and whitespaces
            line = line.split("//")[0].strip()
            if line:
                cleaned_lines.append(line)
        self.cleaned_lines = cleaned_lines
        self.cur_line = None
        self.cur_line_index = 0

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        if self.cur_line_index < len(self.cleaned_lines):
            return True
        return False

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current 
        command. Should be called only if has_more_commands() is true. Initially
        there is no current command.
        """
        if self.has_more_commands():
            self.cur_line = self.cleaned_lines[self.cur_line_index]
            self.cur_line_index += 1

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current VM command.
            "C_ARITHMETIC" is returned for all arithmetic commands.
            For other commands, can return:
            "C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION",
            "C_RETURN", "C_CALL".
        """
        
        command = self.cur_line.split()[0]
        return VM_COMMANDS_TO_TYPE_MAP[command]

    def arg1(self) -> str:
        """
        Returns:
            str: the first argument of the current command. In case of 
            "C_ARITHMETIC", the command itself (add, sub, etc.) is returned. 
            Should not be called if the current command is "C_RETURN".
        """
        
        # split the line to tokens
        line = self.cur_line.split()
     
        command = line[0]
        # TODO: MOVE THE CHECK TO func: translate_file
        # if VM_COMMANDS_TO_TYPE_MAP[command] != CommandType.C_RETURN.value:
        if VM_COMMANDS_TO_TYPE_MAP[command] == CommandType.C_ARITHMETIC.value:
            return command
        return line[1]

    def arg2(self) -> int:
        """
        Returns:
            int: the second argument of the current command. Should be
            called only if the current command is "C_PUSH", "C_POP", 
            "C_FUNCTION" or "C_CALL".
        """
        line = self.cur_line.split()
        return line[2]
