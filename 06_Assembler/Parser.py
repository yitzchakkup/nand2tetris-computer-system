"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

A_INSTRUCTION = '@'
L_INSTRUCTION = '('
C_INSTRUCTION = 'C'


class Parser:

    """Encapsulates access to the input code. Reads an assembly program
    by reading each command line-by-line, parses the current command,
    and provides convenient access to the commands components (fields
    and symbols). In addition, removes all white space and comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.

        Args:
            input_file (typing.TextIO): input file.
        """
        # Your code goes here!
        # A good place to start is to read all the lines of the input:
        # input_lines = input_file.read().splitlines()
        input_lines = input_file.read().splitlines()
        self.input_lines = input_lines
        self.num_commands = len(input_lines)
        self.cur = -1

        self.cur_instruction = None

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        self.cur += 1
        while self.cur < self.num_commands:
            for char in self.input_lines[self.cur]:
                if char == '/':  # It's documentation
                    break  # go to next line
                if char != ' ':
                    return True
            self.cur += 1
        return False

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current command.
        Should be called only if has_more_commands() is true.
        """
        result = ""
        
        for char in self.input_lines[self.cur]:
            if char == ' ':
                continue

            if char == '/':
                break
            # else part of code
            result += char
        self.cur_instruction = result

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current command:
            "A_COMMAND" for @Xxx where Xxx is either a symbol or a decimal number
            "C_COMMAND" for dest=comp;jump
            "L_COMMAND" (actually, pseudo-command) for (Xxx) where Xxx is a symbol
        """
        # Your code goes here!
        if self.cur_instruction[0] == '@':
            return A_INSTRUCTION
        elif self.cur_instruction[0] == '(':
            return L_INSTRUCTION
        else:
            return C_INSTRUCTION

    def symbol(self) -> str:
        """
        Returns:
            str: the symbol or decimal Xxx of the current command @Xxx or
            (Xxx). Should be called only when command_type() is "A_COMMAND" or 
            "L_COMMAND".
        """
        symble = ""
        for char in self.cur_instruction:
            if (char != '(') and (char != ')') and (char != '@'):
                symble += char
        return symble

    def dest(self) -> str:
        """
        Returns:
            str: the dest mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        dest = ""
        i = 0
        while i < len(self.cur_instruction):
            if self.cur_instruction[i] == '=':
                return dest
            dest += self.cur_instruction[i]
            i += 1
        return "null"

    def comp(self) -> str:
        """
        Returns:
            str: the comp mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        comp = ""
        i = 0
        while i < len(self.cur_instruction):
            if self.cur_instruction[i] == '=':
                comp = ""
                i += 1
                continue
            if self.cur_instruction[i] == ';':
                return comp
            comp += self.cur_instruction[i]
            i += 1
        return comp

    def jump(self) -> str:
        """
        Returns:
            str: the jump mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        i = 0
        while i < len(self.cur_instruction):
            if self.cur_instruction[i] == ';':
                return self.cur_instruction[i+1:]
            i += 1
        return "null"
