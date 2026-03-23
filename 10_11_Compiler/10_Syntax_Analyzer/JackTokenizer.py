"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


KEYWORDS = [
    "class", "constructor", "function", "method", "field", "static", "var",
    "int", "char", "boolean", "void", "true", "false", "null", "this",
    "let", "do", "if", "else", "while", "return"
]

SYMBOLS = [
    "{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-", "*", "/", "&",
    "|", "<", ">", "=", "~", "^", "#"
]


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    
    # Jack Language Grammar

    A Jack file is a stream of characters. If the file represents a
    valid program, it can be tokenized into a stream of valid tokens. The
    tokens may be separated by an arbitrary number of whitespace characters, 
    and comments, which are ignored. There are three possible comment formats: 

    """

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        # Your code goes here!
        # A good place to start is to read all the lines of the input:
        input_lines = input_stream.read().splitlines()
        self.cleaned_lines = self._process_lines(input_lines)

        self.cur_line = 0
        self.cur_line_placement = 0
        self.cur_token = None

    def _process_lines(self, input_lines: list[str]) -> list[str]:
        cleaned_lines = []
        is_comment = False
        is_string = False
        
        for line in input_lines:
            clean_line = ''
            index = 0

            while index < len(line):
                if not is_string and not is_comment:
                    # Check for the start of a string literal
                    if line[index] == '"':
                        is_string = True
                        clean_line += line[index]
                    # Check for single-line comment '//'
                    elif line.startswith('//', index):
                        break
                    # Check for the start of a block comment '/*'
                    elif line.startswith('/*', index):
                        is_comment = True
                        index += 1  # Skip the asterisk
                    else:
                        clean_line += line[index]
                elif is_string:
                    clean_line += line[index]
                    # Check for the end of a string literal
                    if line[index] == '"':
                        is_string = False
                elif is_comment:
                    # Check for the end of a block comment '*/'
                    if line.startswith('*/', index):
                        is_comment = False
                        index += 1  # Skip the asterisk
                
                index += 1

            clean_line = clean_line.strip()
            if clean_line and not is_comment: # todo check why is comment needed
                cleaned_lines.append(clean_line)

        return cleaned_lines

# Example use:
# with open("your_file.jack", "r") as file:
#     tokenizer = JackTokenizer(file)

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        while self.cur_line < len(self.cleaned_lines):
            while self.cur_line_placement < len(self.cleaned_lines[self.cur_line]):
                is_token = (self.cleaned_lines[self.cur_line])[self.cur_line_placement]

                if is_token == " " or is_token == "\t":
                    self.cur_line_placement += 1
                else:
                    return True
            # line was 'empty' meaning only white spaces
            self.cur_line += 1
            self.cur_line_placement = 0

        return False

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        # In my implementation I can assume (cleaned_lines[cur_line])[cur_line_placement] != " "
        # because i enforce it.
        if self.has_more_tokens():
            cur_token_line = self.cleaned_lines[self.cur_line]
            token_pointer = cur_token_line[self.cur_line_placement:]
            keyword = token_pointer.split()[0]

            if token_pointer[0] in SYMBOLS:
                self.cur_token = token_pointer[0]
                self.cur_line_placement += 1

            elif keyword in KEYWORDS:
                self.cur_token = keyword
                self.cur_line_placement += len(keyword)

            elif token_pointer[0] == '"':  # it's a stringConst
                # self.advance_string_const()
                self.cur_token = '"'
                self.cur_line_placement += 1
                for let in token_pointer[1:]:
                    self.cur_token += let
                    self.cur_line_placement += 1
                    if let == '"':
                        break  # enf of stringConst

            elif token_pointer[0].isdigit():
                self.cur_token = ""
                for let in token_pointer:
                    if let.isdigit():
                        self.cur_token += let
                        self.cur_line_placement += 1
                    else:
                        break

            else:  # It's an identifier
                self.cur_token = ""
                for let in token_pointer:
                    if let.isdigit() or let.isalpha() or let == '_':
                        self.cur_token += let
                        self.cur_line_placement += 1
                    else:
                        break

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        if self.cur_token in KEYWORDS:
            return "KEYWORD"
        elif self.cur_token in SYMBOLS:
            return "SYMBOL"
        elif self.cur_token.isdigit():
            return "INT_CONST"
        elif self.cur_token and self.cur_token[0] == '"':
            return "STRING_CONST"
        else:
            return "IDENTIFIER"

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        return self.cur_token.upper()

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
            Recall that symbol was defined in the grammar like so:
            symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
        """
        return self.cur_token

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
            Recall that identifiers were defined in the grammar like so:
            identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.
        """
        return self.cur_token

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
            Recall that integerConstant was defined in the grammar like so:
            integerConstant: A decimal number in the range 0-32767.
        """
        return int(self.cur_token)

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
            Recall that StringConstant was defined in the grammar like so:
            StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
        """
        return self.cur_token[1:-1]
    
