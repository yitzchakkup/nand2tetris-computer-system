"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from enum import Enum
from Parser import CommandType


class Segment(Enum):
    ARGUMENT = "argument"
    LOCAL = "local"
    STATIC = "static"
    CONSTANT = "constant"
    THIS = "this"
    THAT = "that"
    POINTER = "pointer"
    TEMP = "temp"


SEGMENT_TO_HACK_SYMBOL_MAP = {
    "R0": "0",  # SP
    "local": "1",  # LCL
    "argument": "2",  # ARG
    "this": "3",      # THIS
    "that": "4",          # THAT
    "temp": "5",
    "static": "16",
    "constant": "",
    "pointer": "3"  # pointer [3,4] fixed segment. pointer to THIS or THAT / TEMPARRY until project 8
}


class CodeWriter:
    """Translates VM commands into Hack assembly code."""
    label_counter = 0
    call_counter = 0
    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """

        self.output_stream = output_stream

        # current file name being translated
        self.file_name = None
        #self.label_counter = 0

        self.cur_function = "OS"
        #self.call_counter = 0

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is 
        started.

        Args:
            filename (str): The name of the VM file.
        """
        # Your code goes here!
        # This function is useful when translating code that handles the
        # static segment. For example, in order to prevent collisions between two
        # .vm files which push/pop to the static segment, one can use the current
        # file's name in the assembly variable's name and thus differentiate between
        # static variables belonging to different files.
        # To avoid problems with Linux/Windows/MacOS differences with regards
        # to filenames and paths, you are advised to parse the filename in
        # the function "translate_file" in Main.py using python's os library,
        # For example, using code similar to:
        # input_filename, input_extension = os.path.splitext(os.path.basename(input_file.name))

        # NOTE: PARSING FILE NAME IN :def translate_file
        self.file_name = filename

    def a_pus_b_neg(self, compere: str):  # a-b >0
        if compere == "LT":
            # set *SP to true
            self.output_stream.write("@0\n")
            self.output_stream.write("A=M-1\n")
            self.output_stream.write("M=-1\n")
        elif compere == "GT" or compere == "EQ":
            # set *SP to false
            self.output_stream.write("@0\n")
            self.output_stream.write("A=M-1\n")
            self.output_stream.write("M=0\n")

    def a_neg_b_pus(self, compere: str):  # a-b <0
        if compere == "GT":
            # set *SP to true
            self.output_stream.write("@0\n")
            self.output_stream.write("A=M-1\n")
            self.output_stream.write("M=-1\n")
        elif compere == "LT" or compere == "EQ":
            # set *SP to false
            self.output_stream.write("@0\n")
            self.output_stream.write("A=M-1\n")
            self.output_stream.write("M=0\n")

    def a_b_same_sign(self, compere: str):
        self.output_stream.write("@SP\n")
        self.output_stream.write("A=M\n")

        self.output_stream.write("D=M\n")   # D = a
        self.output_stream.write("A=A-1\n")
        self.output_stream.write("D=M-D\n")  # D = b - a

        self.output_stream.write("@SP\n")       # Set A register to 0
        self.output_stream.write("A=M-1\n")
        self.output_stream.write("M=-1\n")

        self.output_stream.write("@TRUE_LABEL{}\n".format(CodeWriter.label_counter))
        self.output_stream.write("D;J{}\n".format(compere))

        # if reached here then compare gives false
        self.output_stream.write("@0\n")
        self.output_stream.write("A=M-1\n")
        self.output_stream.write("M=0\n")

        self.output_stream.write("(TRUE_LABEL{})\n".format(CodeWriter.label_counter))

    def print_by_sign(self, compere: str):
        self.output_stream.write("@SP\n")
        self.output_stream.write("A=M\n")
        self.output_stream.write("D=M\n")   # D = y
        self.output_stream.write("@a_positive{}\n".format(CodeWriter.label_counter))
        self.output_stream.write("D;JGT\n")

        # a_negative:
        self.output_stream.write("@SP\n")
        self.output_stream.write("A=M-1\n")
        self.output_stream.write("D=M\n")   # D = y
        self.output_stream.write("@same_sign{}\n".format(CodeWriter.label_counter))
        self.output_stream.write("D;JLT\n")  # b negitive

        # if got here then a<0, b>0
        self.a_neg_b_pus(compere)
        self.output_stream.write("@DONE{}\n".format(CodeWriter.label_counter))
        self.output_stream.write("0;JMP\n")

        # a_positive:
        self.output_stream.write("(a_positive{})\n".format(CodeWriter.label_counter))
        self.output_stream.write("@SP\n")
        self.output_stream.write("A=M-1\n")
        self.output_stream.write("D=M\n")   # D = y
        self.output_stream.write("@same_sign{}\n".format(CodeWriter.label_counter))
        self.output_stream.write("D;JGT\n")  # b positive

        # if got here a>0, b<0
        self.a_pus_b_neg(compere)
        self.output_stream.write("@DONE{}\n".format(CodeWriter.label_counter))
        self.output_stream.write("0;JMP\n")

        self.output_stream.write("(same_sign{})\n".format(CodeWriter.label_counter))
        self.a_b_same_sign(compere)

        self.output_stream.write("(DONE{})\n".format(CodeWriter.label_counter))

        CodeWriter.label_counter += 1

    def write_lt(self):
        # debugging
        self.output_stream.write("//lt\n")

        self.output_stream.write("@SP\n")
        self.output_stream.write("M=M-1\n")

        self.print_by_sign("LT")

    def write_gt(self):
        # debugging
        self.output_stream.write("//gt\n")

        self.output_stream.write("@SP\n")
        self.output_stream.write("M=M-1\n")

        self.print_by_sign("GT")

    def write_eq(self):
        # debugging
        self.output_stream.write("//eq\n")

        self.output_stream.write("@SP\n")
        self.output_stream.write("M=M-1\n")

        self.print_by_sign("EQ")

    def write_sub(self):
        self.output_stream.write("//sub\n")
        self.output_stream.write("@SP\n")
        self.output_stream.write("M=M-1\n")
        self.output_stream.write("A=M\n")
        self.output_stream.write("D=M\n")
        self.output_stream.write("A=A-1\n")
        self.output_stream.write("M=M-D\n")

    def write_add(self):
        self.output_stream.write("// add\n") 
        self.output_stream.write("@SP\n")
        self.output_stream.write("M=M-1\n")
        self.output_stream.write("A=M\n")
        self.output_stream.write("D=M\n")
        self.output_stream.write("A=A-1\n")
        self.output_stream.write("M=D+M\n")

    def write_neg(self):
        self.output_stream.write("// neg\n") 
        self.output_stream.write("@SP\n")
        self.output_stream.write("A=M-1\n")
        self.output_stream.write("M=-M\n")

    def write_and(self):
        self.output_stream.write("//and\n")
        self.output_stream.write("@SP\n")
        self.output_stream.write("M=M-1\n")
        self.output_stream.write("A=M\n")
        self.output_stream.write("D=M\n")
        self.output_stream.write("A=A-1\n")
        self.output_stream.write("M=D&M\n")

    def write_or(self):
        self.output_stream.write("// or\n")
        self.output_stream.write("@SP\n")
        self.output_stream.write("M=M-1\n")
        self.output_stream.write("A=M\n")
        self.output_stream.write("D=M\n")
        self.output_stream.write("A=A-1\n")
        self.output_stream.write("M=D|M\n")

    def write_not(self):
        self.output_stream.write("// not\n")        
        self.output_stream.write("@0\n")  # RAM[0] FOR SP
        self.output_stream.write("A=M-1\n")
        self.output_stream.write("M=!M\n")


# todo check if correct shift left and right
    def write_shiftleft(self):
        """implement shift left command
        """
        self.output_stream.write("// shiftleft\n")
        self.output_stream.write("@0\n")  # RAM[0] FOR SP
        self.output_stream.write("A=M-1\n")
        self.output_stream.write("D=M\n")
        self.output_stream.write("M=D+M\n")

    def write_shiftright(self):
        self.output_stream.write("// shiftright\n")
        self.output_stream.write("@0\n")  # RAM[0] FOR SP
        self.output_stream.write("A=M-1\n")
        self.output_stream.write("M>>\n")

    def write_arithmetic(self, command: str) -> None:
        """Writes assembly code that is the translation of the given 
        arithmetic command. For the commands eq, lt, gt, you should correctly
        compare between all numbers our computer supports, and we define the
        value "true" to be -1, and "false" to be 0.

        Args:
            command (str): an arithmetic command.
        """
        # stage 1: stack arithmetic 

        if command == "not":
            # bit-wise not the value at the top of the stack
            self.write_not()
        elif command == "or":
            # perform or bitwise on the top value of the stack
            self.write_or()
        elif command == "and":
            # perform and bitwise on the top value of the stack
            self.write_and()
        elif command == "neg":
            # negate the value at the top of the stack
            self.write_neg()
        elif command == "add":
            self.write_add()
        elif command == "sub":
            self.write_sub()
        # for logical commands : eq, gt, lt we will treat 
        # true -1 , false 0
        elif command == "eq":
            self.write_eq()
        elif command == "gt":
            self.write_gt()
        elif command == "lt":
            self.write_lt()

        elif command == "shiftleft":
            self.write_shiftleft()
        elif command == "shiftright":
            self.write_shiftright()

    def write_pointer(self, command: str, index: int):
        self.output_stream.write("// {} pointer {}\n".format(command, index))
        if int(index) == 0:  # then we sent to THIS segment
            pointer_value = SEGMENT_TO_HACK_SYMBOL_MAP["this"]
        elif int(index) == 1:  # index == 1
            pointer_value = SEGMENT_TO_HACK_SYMBOL_MAP["that"]
        else:
            pointer_value = str(int(SEGMENT_TO_HACK_SYMBOL_MAP["this"])+index)

        if command == "C_PUSH":
            self.output_stream.write("@{}\n".format(pointer_value))
            self.output_stream.write("D=M\n")
            self.output_stream.write("@SP\n")
            self.output_stream.write("A=M\n")
            self.output_stream.write("M=D\n")
            self.output_stream.write("@SP\n")
            self.output_stream.write("M=M+1\n")
        elif command == "C_POP":
            self.output_stream.write("@SP\n")
            self.output_stream.write("M=M-1\n")
            self.output_stream.write("A=M\n")
            self.output_stream.write("D=M\n")
            self.output_stream.write("@{}\n".format(pointer_value))
            self.output_stream.write("M=D\n")

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes assembly code that is the translation of the given
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """

        # map the segment name to Hack symbol
        segment_symbol = SEGMENT_TO_HACK_SYMBOL_MAP[segment]

        # special value for pointer
        if segment == "pointer":
            self.write_pointer(command, index)

        # if it's push constant i
        elif segment == "constant":
            self.output_stream.write("// push constant {}\n".format(index))
            self.output_stream.write("@{}\n".format(index))
            self.output_stream.write("D=A\n")
            self.output_stream.write("@SP\n")
            self.output_stream.write("A=M\n")
            self.output_stream.write("M=D\n")
            self.output_stream.write("@SP\n")
            self.output_stream.write("M=M+1\n")

        elif command == "C_PUSH":
            self.output_stream.write("// push {} {}\n".format(segment, index))

            # handling naming convention for static variables
            if segment == "static":
                # A = file_name.index
                self.output_stream.write("@{}.{}\n".format(self.file_name, index))
            elif segment == "temp":
                self.output_stream.write("@{}\n".format(segment_symbol))
                # D= ram[segment]
                self.output_stream.write("D=A\n")
                self.output_stream.write("@{}\n".format(index))
                self.output_stream.write("A=D+A\n")

            else:
                # ram[segment]
                self.output_stream.write("@{}\n".format(segment_symbol))
                # D= ram[segment]
                self.output_stream.write("D=M\n")
                self.output_stream.write("@{}\n".format(index))
                self.output_stream.write("A=D+A\n")

            # continue instruction
            self.output_stream.write("D=M\n")
            self.output_stream.write("@SP\n")
            self.output_stream.write("A=M\n")
            self.output_stream.write("M=D\n")
            self.output_stream.write("@SP\n")
            self.output_stream.write("M=M+1\n")

        # else it's a pop command
        elif command == "C_POP":
            self.output_stream.write("// pop {} {}\n".format(segment, index))

            # handling naming convention for static variables (xxx.index)
            if segment == "static":
                self.output_stream.write("@{}.{}\n".format(self.file_name, index))
                self.output_stream.write("D=A\n")
            elif segment == "temp":
                self.output_stream.write("@{}\n".format(segment_symbol))
                self.output_stream.write("D=A\n")
                self.output_stream.write("@{}\n".format(index))
                self.output_stream.write("D=D+A\n")
            else:
                # accessing SEGMENT location
                self.output_stream.write("@{}\n".format(segment_symbol))
                self.output_stream.write("D=M\n")
                self.output_stream.write("@{}\n".format(index))
                self.output_stream.write("D=D+A\n")

            # continue instructions
            self.output_stream.write("@13\n")
            self.output_stream.write("M=D\n")
            self.output_stream.write("@SP\n")
            self.output_stream.write("AM=M-1\n")
            self.output_stream.write("D=M\n")
            self.output_stream.write("@13\n")
            self.output_stream.write("A=M\n")
            self.output_stream.write("M=D\n")

    def write_label(self, label: str) -> None:
        """Writes assembly code that affects the label command. 
        Let "Xxx.foo" be a function within the file Xxx.vm. The handling of
        each "label bar" command within "Xxx.foo" generates and injects the symbol
        "Xxx.foo$bar" into the assembly code stream.
        When translating "goto bar" and "if-goto bar" commands within "foo",
        the label "Xxx.foo$bar" must be used instead of "bar".

        Args:
            label (str): the label to write.
        """
        self.output_stream.write("// label {}${}\n".format(self.cur_function, label))
        self.output_stream.write("({}.{}${})\n".format(self.file_name, self.cur_function, label))

    def write_goto(self, label: str) -> None:
        """Writes assembly code that affects the goto command.

        Args:
            label (str): the label to go to.
        """
        self.output_stream.write("// goto {}${}\n".format(self.cur_function, label))
        self.output_stream.write("@{}.{}${}\n".format(self.file_name, self.cur_function, label))
        self.output_stream.write("0;JMP\n")

    def write_if(self, label: str) -> None:
        """Writes assembly code that affects the if-goto command. 

        Args:
            label (str): the label to go to.
        """
        self.output_stream.write("// if goto {}${}\n".format(self.cur_function, label))
        # checking if last element in stack is true (-1)
        self.output_stream.write("@SP\n")
        self.output_stream.write("M=M-1\n")
        self.output_stream.write("A=M\n")
        self.output_stream.write("D=M\n")

        self.output_stream.write("@SKIP.{}\n".format(CodeWriter.label_counter))
        self.output_stream.write("D;JEQ\n")

        # last element in SP is -1 (positive) so jump.
        self.output_stream.write("@{}.{}${}\n".format(self.file_name, self.cur_function, label))
        self.output_stream.write("0;JMP\n")

        self.output_stream.write("(SKIP.{})\n".format(CodeWriter.label_counter))

        CodeWriter.label_counter += 1
    
    def write_function(self, function_name: str, n_vars: int) -> None:
        """Writes assembly code that affects the function command. 
        The handling of each "function Xxx.foo" command within the file Xxx.vm
        generates and injects a symbol "Xxx.foo" into the assembly code stream,
        that labels the entry-point to the function's code.
        In the subsequent assembly process, the assembler translates this 
        symbol into the physical address where the function code starts.

        Args:
            function_name (str): the name of the function.
            n_vars (int): the number of local variables of the function.
        """
        # The pseudo-code of "function function_name n_vars" is:
        # (function_name)       // injects a function entry label into the code
        # repeat n_vars times:  // n_vars = number of local variables
        #   push constant 0     // initializes the local variables to 0
        self.cur_function = function_name

        self.output_stream.write("// function {}\n".format(self.cur_function))
        self.output_stream.write("({})\n".format(self.cur_function))

        for i in range(int(n_vars)):
            self.write_push_pop(CommandType.C_PUSH.value, "constant", 0)

        self.output_stream.write("//end function {}.{} declaration\n".format(self.file_name, self.cur_function))

    def hack_push_any_value(self, element: str):
        self.output_stream.write(element+"\n")  # element to push
        self.output_stream.write("D=A\n")
        self.output_stream.write("@SP\n")
        self.output_stream.write("M=M+1\n")
        self.output_stream.write("A=M-1\n")
        self.output_stream.write("M=D\n")

    def hack_push_value_from_pointer(self, pointer: str):
        self.output_stream.write("@"+pointer+"\n")
        # self.output_stream.write("A=M\n")
        self.output_stream.write("D=M\n")
        self.output_stream.write("@SP\n")
        self.output_stream.write("M=M+1\n")
        self.output_stream.write("A=M-1\n")
        self.output_stream.write("M=D\n")

    def hack_reposition_ARG(self, arg_pointer: str, n: int):
        """
        repositions ARG to SP-5-n_args
        :param arg_pointer:
        :param n:
        :return:
        """
        self.output_stream.write("@SP\n")
        self.output_stream.write("D=M\n")
        self.output_stream.write("@5\n")
        self.output_stream.write("D=D-A\n")
        self.output_stream.write("@{}\n".format(n))
        self.output_stream.write("D=D-A\n")

        self.output_stream.write("@"+arg_pointer+"\n")
        self.output_stream.write("M=D\n")

    def write_call(self, function_name: str, n_args: int) -> None:
        """Writes assembly code that affects the call command. 
        Let "Xxx.foo" be a function within the file Xxx.vm.
        The handling of each "call" command within Xxx.foo's code generates and
        injects a symbol "Xxx.foo$ret.i" into the assembly code stream, where
        "i" is a running integer (one such symbol is generated for each "call"
        command within "Xxx.foo").
        This symbol is used to mark the return address within the caller's 
        code. In the subsequent assembly process, the assembler translates this
        symbol into the physical memory address of the command immediately
        following the "call" command.

        Args:
            function_name (str): the name of the function to call.
            n_args (int): the number of arguments of the function.
        """
        # The pseudo-code of "call function_name n_args" is:
        # push return_address   // generates a label and pushes it to the stack
        # push LCL              // saves LCL of the caller
        # push ARG              // saves ARG of the caller
        # push THIS             // saves THIS of the caller
        # push THAT             // saves THAT of the caller
        # ARG = SP-5-n_args     // repositions ARG
        # LCL = SP              // repositions LCL
        # goto function_name    // transfers control to the callee
        # (return_address)      // injects the return address label into the code
        self.output_stream.write("//call function {}.{}\n".format(self.file_name, function_name))

        # pushing return_address, LCL, ARG, THIS, and THAT for safe keeping
        return_address = "@{}.{}$ret.{}".format(self.file_name, function_name, CodeWriter.call_counter)
        self.output_stream.write("//push return_address\n")
        self.hack_push_any_value(return_address)

        self.output_stream.write("//push LCL\n")
        self.hack_push_value_from_pointer("LCL")
        self.output_stream.write("//push ARG\n")
        self.hack_push_value_from_pointer("ARG")
        self.output_stream.write("//push THIS\n")
        self.hack_push_value_from_pointer("THIS")
        self.output_stream.write("//push THAT\n")
        self.hack_push_value_from_pointer("THAT")

        # ARG = SP-5-n_args
        self.output_stream.write("//ARG = SP-5-n_args\n")
        self.hack_reposition_ARG("ARG", n_args)

        # LCL = SP
        self.output_stream.write("//LCL = SP\n")
        self.output_stream.write("@SP\n")
        self.output_stream.write("D=M\n")
        self.output_stream.write("@LCL\n")
        self.output_stream.write("M=D\n")

        # goto function_name
        self.output_stream.write("//goto function_name\n")
        self.output_stream.write("@{}\n".format(function_name))
        self.output_stream.write("0;JMP\n")

        # After the function returns to hear
        self.output_stream.write("//(return_address)\n")
        self.output_stream.write("({}.{}$ret.{})\n".format(self.file_name, function_name, CodeWriter.call_counter))
        CodeWriter.call_counter += 1
        self.output_stream.write("//End of call function {}.{}\n".format(self.file_name, function_name))

    def write_return(self) -> None:
        """Writes assembly code that affects the return command."""
        # The pseudo-code of "return" is:
        # frame = LCL                   // frame is a temporary variable
        # return_address = *(frame-5)   // puts the return address in a temp var
        # *ARG = pop()                  // repositions the return value for the caller
        # SP = ARG + 1                  // repositions SP for the caller
        # THAT = *(frame-1)             // restores THAT for the caller
        # THIS = *(frame-2)             // restores THIS for the caller
        # ARG = *(frame-3)              // restores ARG for the caller
        # LCL = *(frame-4)              // restores LCL for the caller
        # goto return_address           // go to the return address
        self.output_stream.write("//return function {}.{}\n".format(self.file_name, self.cur_function))

    # frame/@15 = LCL
        self.output_stream.write("//frame/@15 = LCL\n")
        self.output_stream.write("@LCL\n")
        self.output_stream.write("D=M\n")
        self.output_stream.write("@15\n")
        self.output_stream.write("M=D\n")

        # return_address/@14 = *(frame-5)
        self.output_stream.write("//return_address/@14 = *(frame-5)\n")
        self.output_stream.write("@5\n")
        self.output_stream.write("D=A\n")
        self.output_stream.write("@LCL\n")
        self.output_stream.write("A=M-D\n")
        self.output_stream.write("D=M\n")
        self.output_stream.write("@14\n")
        self.output_stream.write("M=D\n")

        # *ARG = pop()
        self.output_stream.write("//# *ARG = pop()\n")
        self.write_push_pop(CommandType.C_POP.value, "argument", 0)

        # SP = ARG + 1
        self.output_stream.write("//SP = ARG + 1\n")
        self.output_stream.write("@ARG\n")
        self.output_stream.write("D=M\n")
        self.output_stream.write("@SP\n")
        self.output_stream.write("M=D+1\n")

        # THAT = *(frame-1),  THIS = *(frame-2),  ARG = *(frame-3),  LCL = *(frame-4)
        for index, segment in enumerate(["THAT", "THIS", "ARG", "LCL"]):
            self.output_stream.write("//{} = *(frame-{})\n".format(segment, index+1))
            self.output_stream.write("@15\n")  # frame
            self.output_stream.write("M=M-1\n")
            self.output_stream.write("A=M\n")
            self.output_stream.write("D=M\n")
            self.output_stream.write("@{}\n".format(segment))  # THAT/THIS/ARG/LCL
            self.output_stream.write("M=D\n")

        # goto return_address
        self.output_stream.write("//goto return_address\n")
        self.output_stream.write("@14\n")
        self.output_stream.write("A=M\n")
        self.output_stream.write("0;JMP\n")
