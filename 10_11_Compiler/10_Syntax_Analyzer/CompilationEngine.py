"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import JackTokenizer


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: "JackTokenizer", output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.token_generator = input_stream
        self.output = output_stream
        self.space_count = 0

        # Prepare tokenizer
        if self.token_generator.has_more_tokens():
            self.token_generator.advance()

    def _write_xml_line(self, token_type: str, token_content: str) -> None:
        """Writes a single XML element with the current content and tag name."""
        escaped_content = (token_content.replace("&", "&amp;")
                                         .replace("<", "&lt;")
                                         .replace(">", "&gt;")
                                         .replace('"', '&quot;'))
        self.output.write(f'{"  " * self.space_count}<{token_type}> {escaped_content} </{token_type}>\n')

    def _open_tag(self, tag_name: str) -> None:
        """Writes an opening tag for a given XML structure."""
        self.output.write(f'{"  " * self.space_count}<{tag_name}>\n')
        self.space_count += 1

    def _close_tag(self, tag_name: str) -> None:
        """Writes a closing tag for a given XML structure."""
        self.space_count -= 1
        self.output.write(f'{"  " * self.space_count}</{tag_name}>\n')

    def compile_class(self) -> None:
        """Compiles a complete class."""
        self._open_tag('class')
        self._compile_class_declaration()
        self._compile_class_body()
        self._close_tag('class')
        self.token_generator.advance()

    def _compile_class_declaration(self) -> None:
        """Compiles the declaration part of a class."""
        self._compile_keyword()  # 'class'
        self.token_generator.advance()
        self._compile_identifier()  # class name
        self.token_generator.advance()
        self._compile_symbol()  # '{'
        self.token_generator.advance()

    def _compile_class_body(self) -> None:
        """Compiles the body of a class."""
        while self.token_generator.has_more_tokens():
            if self.token_generator.keyword() in ['STATIC', 'FIELD']:
                self.compile_class_var_dec()
            elif self.token_generator.keyword() in ['CONSTRUCTOR', 'FUNCTION', 'METHOD']:
                self.compile_subroutine()
            else:
                self.token_generator.advance()
        self._compile_symbol()  # '}'

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        self._open_tag('classVarDec')
        self._compile_keyword()  # 'static' or 'field'
        self.token_generator.advance()

        # Type could be a keyword or a class name (identifier)
        if self.token_generator.token_type() == "KEYWORD":
            self._compile_keyword()  # 'int', 'char', 'boolean'
        else:
            self._compile_identifier()  # Class type name
        self.token_generator.advance()

        self._compile_identifier()  # First varName
        self.token_generator.advance()

        # Handle additional varNames separated by commas
        while self.token_generator.symbol() == ',':
            self._compile_symbol()  # ','
            self.token_generator.advance()
            self._compile_identifier()  # Additional varName
            self.token_generator.advance()

        self._compile_symbol()  # ';'
        self.token_generator.advance()
        self._close_tag('classVarDec')

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """

        self._open_tag('subroutineDec')
        self._compile_keyword()
        self.token_generator.advance()

        # Check whether it's a keyword type or an identifier type.
        if self.token_generator.token_type() == "KEYWORD":
            self._compile_keyword()  # 'void' or other primitive type
        elif self.token_generator.token_type() == "IDENTIFIER":
            self._compile_identifier()  # custom return type
        self.token_generator.advance()

        # Compiles the subroutine name.
        self._compile_identifier()  # subroutine name
        self.token_generator.advance()
        self._compile_symbol()  # '('
        self.token_generator.advance()
        self.compile_parameter_list()
        self._compile_symbol()  # ')'
        self.token_generator.advance()

        # Subroutine body.
        self._open_tag('subroutineBody')
        self._compile_symbol()  # '{'
        self.token_generator.advance()

        # Variable declarations.
        while self.token_generator.token_type() == "KEYWORD" and self.token_generator.keyword() == 'VAR':
            self.compile_var_dec()

        # Statements.
        self.compile_statements()
        self._compile_symbol()  # '}'
        self.token_generator.advance()
        self._close_tag('subroutineBody')

        self._close_tag('subroutineDec')

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the enclosing "()".
        """
        self._open_tag('parameterList')
        while self.token_generator.token_type() != "SYMBOL" or self.token_generator.symbol() != ")":
            # Check if the token is a keyword type or a class type identifier.
            if self.token_generator.token_type() == "KEYWORD":
                self._compile_keyword()  # type keyword like 'int', 'char', 'boolean'
            elif self.token_generator.token_type() == "IDENTIFIER":
                self._compile_identifier()  # type identifier like 'Unary', which is the type of the parameter

            self.token_generator.advance()  # Advance after writing the type
            self._compile_identifier()  # varName, the name of the parameter
            self.token_generator.advance()  # Advance after writing the varName

            # If there is a comma, we have more parameters to write
            if self.token_generator.token_type() == "SYMBOL" and self.token_generator.symbol() == ",":
                self._compile_symbol()  # ','
                self.token_generator.advance()  # Advance after the comma to get to the next parameter type
        self._close_tag('parameterList')

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""

        self._open_tag('varDec')
        self._compile_keyword()  # 'var'
        self.token_generator.advance()

        # The type can be a keyword or an identifier (class name), handle both cases
        if self.token_generator.token_type() == "KEYWORD":
            self._compile_keyword()  # Type (e.g., 'int', 'char', 'boolean')
        elif self.token_generator.token_type() == "IDENTIFIER":
            self._compile_identifier()  # Custom class type
        self.token_generator.advance()

        # Now compile the variable name
        self._compile_identifier()  # varName
        self.token_generator.advance()

        # Handle additional variable names separated by commas
        while self.token_generator.token_type() == "SYMBOL" and self.token_generator.symbol() == ",":
            self._compile_symbol()  # ','
            self.token_generator.advance()
            self._compile_identifier()  # Next varName
            self.token_generator.advance()

        self._compile_symbol()  # ';'
        self.token_generator.advance()
        self._close_tag('varDec')

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing "{}"."""
        self._open_tag('statements')
        while (self.token_generator.token_type() == "KEYWORD" and
               self.token_generator.keyword() in ["LET", "IF", "WHILE", "DO", "RETURN"]):
            if self.token_generator.keyword() == "LET":
                self.compile_let()
            elif self.token_generator.keyword() == "IF":
                self.compile_if()
            elif self.token_generator.keyword() == "WHILE":
                self.compile_while()
            elif self.token_generator.keyword() == "DO":
                self.compile_do()
            elif self.token_generator.keyword() == "RETURN":
                self.compile_return()
            
            # Check for the next statement without prematurely advancing the tokenizer
            if not (self.token_generator.has_more_tokens() and self.token_generator.token_type() == "KEYWORD"):
                break  # Exit loop if no more statements are present

        self._close_tag('statements')

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self._open_tag('doStatement')
        self._compile_keyword()  # 'do'
        self.token_generator.advance()
        self._compile_subroutine_call()
        self._compile_symbol()  # ';'
        self.token_generator.advance()
        self._close_tag('doStatement')

    def compile_let(self) -> None:
        """Compiles a let statement."""
        self._open_tag('letStatement')
        self._compile_keyword()  # 'let'
        self.token_generator.advance()
        self._compile_identifier()  # varName
        self.token_generator.advance()
        if self.token_generator.token_type() == "SYMBOL" and self.token_generator.symbol() == "[":
            self._compile_symbol()  # '['
            self.token_generator.advance()
            self.compile_expression()
            self._compile_symbol()  # ']'
            self.token_generator.advance()
        self._compile_symbol()  # '='
        self.token_generator.advance()
        self.compile_expression()
        self._compile_symbol()  # ';'
        self.token_generator.advance()
        self._close_tag('letStatement')

    def compile_while(self) -> None:
        """Compiles a while statement."""
        self._open_tag('whileStatement')
        self._compile_keyword()  # 'while'
        self.token_generator.advance()
        self._compile_symbol()  # '('
        self.token_generator.advance()
        self.compile_expression()
        self._compile_symbol()  # ')'
        self.token_generator.advance()
        self._compile_symbol()  # '{'
        self.token_generator.advance()
        self.compile_statements()
        self._compile_symbol()  # '}'
        self.token_generator.advance()
        self._close_tag('whileStatement')

    def compile_return(self) -> None:
        """Compiles a return statement."""
        self._open_tag('returnStatement')
        self._compile_keyword()  # 'return'
        self.token_generator.advance()
        if self.token_generator.token_type() != "SYMBOL" or self.token_generator.symbol() != ";":
            self.compile_expression()
        self._compile_symbol()  # ';'
        self.token_generator.advance()
        self._close_tag('returnStatement')

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        self._open_tag('ifStatement')
        self._compile_keyword()  # 'if'
        self.token_generator.advance()
        self._compile_symbol()  # '('
        self.token_generator.advance()
        self.compile_expression()
        self._compile_symbol()  # ')'
        self.token_generator.advance()
        self._compile_symbol()  # '{'
        self.token_generator.advance()
        self.compile_statements()
        self._compile_symbol()  # '}'
        self.token_generator.advance()
        if self.token_generator.token_type() == "KEYWORD" and self.token_generator.keyword() == "ELSE":
            self._compile_keyword()  # 'else'
            self.token_generator.advance()
            self._compile_symbol()  # '{'
            self.token_generator.advance()
            self.compile_statements()
            self._compile_symbol()  # '}'
            self.token_generator.advance()
        self._close_tag('ifStatement')

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self._open_tag('expression')
        self.compile_term()
        while (self.token_generator.token_type() == "SYMBOL" and self.token_generator.symbol() in
               ["+", "-", "*", "/", "&", "|", "<", ">", "="]):
            self._compile_symbol()  # op
            self.token_generator.advance()
            self.compile_term()
        self._close_tag('expression')

    def compile_term(self) -> None:
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        self._open_tag('term')
        token_type = self.token_generator.token_type()
        if token_type == "INT_CONST":
            self._compile_integer_constant()
            self.token_generator.advance()
        elif token_type == "STRING_CONST":
            self._compile_string_constant()
            self.token_generator.advance()
        elif token_type == "KEYWORD":
            self._compile_keyword()  # 'true', 'false', 'null', 'this'
            self.token_generator.advance()
        elif token_type == "IDENTIFIER":
            self._compile_identifier()
            self.token_generator.advance()
            if self.token_generator.token_type() == "SYMBOL" and self.token_generator.symbol() == "[":
                self._compile_symbol()  # '['
                self.token_generator.advance()
                self.compile_expression()
                self._compile_symbol()  # ']'
                self.token_generator.advance()
            elif self.token_generator.token_type() == "SYMBOL" and self.token_generator.symbol() in ["(", "."]:
                if self.token_generator.symbol() == "(":
                    self._compile_symbol()  # '('
                    self.token_generator.advance()
                    self.compile_expression_list()
                    self._compile_symbol()  # ')'
                    self.token_generator.advance()
                else:  # '.'
                    self._compile_symbol()  # '.'
                    self.token_generator.advance()
                    self._compile_identifier()  # subroutineName
                    self.token_generator.advance()
                    self._compile_symbol()  # '('
                    self.token_generator.advance()
                    self.compile_expression_list()
                    self._compile_symbol()  # ')'
                    self.token_generator.advance()
        elif token_type == "SYMBOL":
            symbol = self.token_generator.symbol()
            if symbol == "(":
                self._compile_symbol()  # '('
                self.token_generator.advance()
                self.compile_expression()
                self._compile_symbol()  # ')'
                self.token_generator.advance()
            elif symbol in ["-", "~", "^", "#"]:  # todo I've changed
                self._compile_symbol()  # unaryOp
                self.token_generator.advance()
                self.compile_term()
        self._close_tag('term')
        
    def _compile_subroutine_call(self) -> None:
        """Compiles a subroutine call."""
        self._compile_identifier()  # subroutineName or (className | varName)
        self.token_generator.advance()
        if self.token_generator.symbol() == '.':
            self._compile_symbol()  # '.'
            self.token_generator.advance()
            self._compile_identifier()  # subroutineName
            self.token_generator.advance()
        self._compile_symbol()  # '('
        self.token_generator.advance()
        self.compile_expression_list()
        self._compile_symbol()  # ')'
        self.token_generator.advance()

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        self._open_tag('expressionList')
        if self.token_generator.token_type() != "SYMBOL" or self.token_generator.symbol() != ")":
            self.compile_expression()
            while self.token_generator.token_type() == "SYMBOL" and self.token_generator.symbol() == ",":
                self._compile_symbol()  # ','
                self.token_generator.advance()
                self.compile_expression()
        self._close_tag('expressionList')

    def _compile_keyword(self):
        if self.token_generator.token_type() != "KEYWORD":
            return
        self._write_xml_line('keyword', self.token_generator.keyword().lower())

    def _compile_symbol(self):
        if self.token_generator.token_type() != "SYMBOL":
            return
        self._write_xml_line('symbol', self.token_generator.symbol())

    def _compile_integer_constant(self):
        if self.token_generator.token_type() != "INT_CONST":
            return
        self._write_xml_line('integerConstant', str(self.token_generator.int_val()))

    def _compile_string_constant(self):
        if self.token_generator.token_type() != "STRING_CONST":
            return
        self._write_xml_line('stringConstant', self.token_generator.string_val())

    def _compile_identifier(self):
        if self.token_generator.token_type() != "IDENTIFIER":
            return
        self._write_xml_line('identifier', self.token_generator.identifier())
