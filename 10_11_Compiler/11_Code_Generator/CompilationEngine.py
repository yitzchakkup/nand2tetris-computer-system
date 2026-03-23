from SymbolTable import SymbolTable
from VMWriter import VMWriter
from JackTokenizer import JackTokenizer


arithmetic_vm_symbol_table = {
    "*": "multiply",
    "/": "divide",
    "+": "ADD",
    "&": "AND",
    "|": "OR",
    "<": "LT",
    ">": "GT",
    "=": "EQ",
    # unaryOp:
    "-": "SUB",
    "~": "NOT",
    "^": "SHIFTLEFT",
    "#": "SHIFTRIGHT"
}

class CompilationEngine:
    def __init__(self, token_generator: JackTokenizer, output_stream):
        self.token_generator = token_generator
        self.writer = VMWriter(output_stream)
        self.symbol_table = SymbolTable()
        self.class_name = ""
        # self.active_subroutine_name = ""
        self.label_counter = 0

        self.void = False
        self.CONSTRUCTOR = False

    def compile_class(self):
        # Ensures we are at the beginning of a new class
        self.token_generator.advance()  # Advance to the first token, should be 'class'

        self.token_generator.advance()  # Advance to class name

        self.class_name = self.token_generator.identifier()  # Capture the class name

        self.token_generator.advance()  # Advance to '{', the symbol after class name

        self.token_generator.advance()  # Now at the first class member or subroutine declaration

        # Handle class variable declarations or subroutine declarations next
        while self.token_generator.has_more_tokens():
            keyword = self.token_generator.keyword() 
            if keyword in ('STATIC', 'FIELD'):
                self.compile_class_var_dec()  # Compile class variable declarations
            elif keyword in ('CONSTRUCTOR', 'FUNCTION', 'METHOD'):
                self.compile_subroutine()  # Compile subroutine declarations
            elif self.token_generator.symbol() == '}':
                break  # End of class declaration

    # If token_generator has no more tokens or '}' was found, the class compilation is done.
    def compile_class_var_dec(self):
        kind = self.token_generator.keyword()  # Expect STATIC or FIELD
        self.token_generator.advance()  # Advance to type
        
        type = self.token_generator.keyword() if self.token_generator.token_type() == "KEYWORD" else self.token_generator.identifier()
        self.token_generator.advance()  # Advance to varName
        
        while True:
            name = self.token_generator.identifier()
            self.symbol_table.define(name, type, kind)
            self.token_generator.advance()  # Advance to ',' or ';'
            
            if self.token_generator.symbol() == ";":
                self.token_generator.advance()  # Advance past ';' to the next class variable declaration or subroutine
                break
            self.token_generator.advance()  # past ','

    def compile_subroutine(self):
        self.symbol_table.start_subroutine()

        subroutine_type = self.token_generator.keyword()
        self.token_generator.advance()  # Advance to 'void' or type
        self.CONSTRUCTOR = False
        self.void = False
        if self.token_generator.token_type() == "KEYWORD" and self.token_generator.keyword() == "VOID":
            self.void = True
        self.token_generator.advance()  # Advance to subroutineName
        
        subroutine_name = self.token_generator.identifier()
        full_subroutine_name = f"{self.class_name}.{subroutine_name}"
        # self.writer.write_label(full_subroutine_name)

        self.token_generator.advance()
        self.token_generator.advance()  # '('
        self.compile_parameter_list()
        self.token_generator.advance()  # ')'
        
        self.token_generator.advance()  # '{'

        
        while self.token_generator.has_more_tokens() and self.token_generator.token_type() == "KEYWORD" and self.token_generator.keyword() == "VAR":
            self.compile_var_dec()

        # Validate the number of local variables before writing the function
        var_count = self.symbol_table.var_count("VAR")
        if var_count == -1:
            # If var_count is invalid, skip further processing to avoid incorrect VM code generation
            return

        self.writer.write_function(full_subroutine_name, var_count)

        # Handle 'this' for methods and constructors
        if subroutine_type == "METHOD":
            # in order to make THIS be the first argument (which is the class type of method)
            self.writer.write_push("ARGUMENT", 0)
            self.writer.write_pop("POINTER", 0)

        elif subroutine_type == "CONSTRUCTOR":
            self.CONSTRUCTOR = True
            # constructor creates and puts the corresponding element in THIS
            num_fields = self.symbol_table.var_count("FIELD")
            self.writer.write_push("CONSTANT", num_fields)
            self.writer.write_call("Memory.alloc", 1)
            self.writer.write_pop("POINTER", 0)


        self.compile_statements()
        # self.token_generator.advance()  # Close subroutine body '}'

        self.token_generator.advance()  # past '}' (of class)

    def compile_parameter_list(self):
        # Check for empty parameter list
        if self.token_generator.symbol() != ")":
            while True:
                # Determine if the type is a keyword type or a class type
                type = self.token_generator.keyword().lower() if self.token_generator.token_type() == "KEYWORD" else self.token_generator.identifier()
                
                # Advance to the variable name
                self.token_generator.advance()
                name = self.token_generator.identifier()

                # Define the new argument in the symbol table
                self.symbol_table.define(name, type, "ARG")
                
                # Advance past the variable name
                self.token_generator.advance()
                
                # Check if the current symbol is a comma, indicating more parameters
                if self.token_generator.symbol() == ')':
                    # If it's not a comma, it should be ')', signaling the end of the parameter list
                    break
                else:
                    # Advance to the next parameter's type
                    self.token_generator.advance()  # past ','
            
    def compile_statements(self):
        while self.token_generator.has_more_tokens() and self.token_generator.symbol() != "}":
            # Each statement method called should handle advancing to the correct token
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

                # self.compile_return()
    
            

   
    def compile_var_dec(self):
        self.token_generator.advance()  # Advance to type
        type = self.token_generator.keyword() if self.token_generator.token_type() == "KEYWORD" else self.token_generator.identifier()
        self.token_generator.advance()  # varName
        
        while True:
            name = self.token_generator.identifier()
            self.symbol_table.define(name, type, "VAR")
            self.token_generator.advance()  # ',' or ';'
            if self.token_generator.symbol() == ";":
                self.token_generator.advance()  # Advance past ';' to next token after var declaration
                break
            self.token_generator.advance()  # past ','
            # No need to advance here; the while loop will call advance() at the beginning



    def compile_let(self):
        self.token_generator.advance()  # from let to varName
        var_name = self.token_generator.identifier()
        
        # Check if the variable is defined in the symbol table before proceeding
        var_kind = self.symbol_table.kind_of(var_name)
        var_index = self.symbol_table.index_of(var_name)
        if var_kind is None or var_index == -1:
            self.token_generator.advance()
            return

        self.token_generator.advance()  # it's '=' or '['

        array_access = False
        if self.token_generator.symbol() == "[":
            # Array element assignment
            array_access = True
            self.writer.write_push(self._segment_of(var_kind), var_index)
            self.token_generator.advance()  # expression
            self.compile_expression()  # compile_expression will advance token_generator correctly

            self.writer.write_arithmetic('add')  # Calculate address
            self.token_generator.advance()  # Advance to '='

        self.token_generator.advance()  # expression after '='
        self.compile_expression()  # compile_expression will advance token_generator correctly

        if array_access:
            # If it was an array access, we need to pop the temporary value into 'that'
            self.writer.write_pop('TEMP', 0)  # Temporarily store the value to be assigned
            self.writer.write_pop('POINTER', 1)  # Set 'that' to the array address
            self.writer.write_push('TEMP', 0)  # Push the value back to be assigned
            self.writer.write_pop('THAT', 0)  # Pop the value into the array element
        else:
            # Simple variable assignment
            self.writer.write_pop(self._segment_of(var_kind), var_index)  # Pop the result of the expression into the variable

        self.token_generator.advance()  # Advance past ';' at end of let statement


    def _segment_of(self, kind):
        
        return {
            "STATIC": "STATIC",
            "FIELD": "THIS",
            "ARG": "ARGUMENT",
            "VAR": "LOCAL"
        }.get(kind, "temp")  # Default to "temp" as a safeguard

    def compile_if(self):
        label_if_false = f"IF_FALSE{self.label_counter}"
        label_end = f"IF_END{self.label_counter}"
        self.token_generator.advance()  # 'if'

        self.label_counter += 1  # Increment to ensure labels are unique

        self.token_generator.advance()  # '('
        self.compile_expression()  # compile_expression will advance token_generator correctly
        self.token_generator.advance()  # ')'
        self.writer.write_arithmetic("NOT")

        self.writer.write_if(label_if_false)  # If-goto command for false condition
        self.token_generator.advance()  # '{'
        self.compile_statements()  # compile_statements will advance token_generator correctly
        self.token_generator.advance()  # '}'
        self.writer.write_goto(label_end)

        self.writer.write_label(label_if_false)


        if self.token_generator.has_more_tokens() and self.token_generator.keyword() == "ELSE":
            self.token_generator.advance()  # 'else'
            self.token_generator.advance()  # '{'
            self.compile_statements()  # compile_statements will advance token_generator correctly
            self.token_generator.advance()  # '}'
        
        self.writer.write_label(label_end)
        # No need to advance here, label_end does not consume any tokens

    def compile_while(self):
        label_while_success = f"WHILE_SUCCESS{self.label_counter}"
        label_end = f"WHIlE_END{self.label_counter}"
        self.label_counter += 1  # Increment to ensure labels are unique
        self.token_generator.advance()  # 'while'
        self.writer.write_label(label_while_success)
        self.token_generator.advance()  # '('
        self.compile_expression()  # compile_expression will advance token_generator correctly
        self.token_generator.advance()  #  ')'
        self.writer.write_arithmetic("NOT")

        self.writer.write_if(label_end)  # If-goto command for false condition
        self.token_generator.advance()  # '{'
        self.compile_statements()  # compile_statements will advance token_generator correctly
        self.writer.write_goto(label_while_success)

        self.writer.write_label(label_end)
        self.token_generator.advance()  # Advance past '}' of if block



    def compile_do(self):
            self.token_generator.advance()  # Advance to the subroutine name or a class/var name
            name = self.token_generator.identifier()  # Get the subroutine name
            self.token_generator.advance()  # Advance to either '.' or '('
            self._compile_subroutine_call(name)  # Compile the subroutine call
            self.writer.write_pop("TEMP", 0)  # Discard the subroutine's return value
            self.token_generator.advance()  # Advance past ';' to end the 'do' statement

            #self.token_generator.advance()  # Advance past '}' to the next statement

    def compile_return(self):
        if self.void:
            self.writer.write_push("CONST", 0)
        elif self.CONSTRUCTOR:
            # constructor return current element that was created
            self.writer.write_push("POINTER", 0)
            self.token_generator.advance()  # past 'this'

        self.token_generator.advance()  # Possible expression start or ';'
        if self.token_generator.symbol() != ";":
            self.compile_expression()  # compile_expression will advance token_generator correctly
        # else:
        #     self.writer.write_push("constant", 0)  # Return 0 for void functions
        #
        self.writer.write_return()
        self.token_generator.advance()  # Advance past ';'

    def compile_expression(self):
        if self.token_generator.token_type() in ["INT_CONST", "IDENTIFIER","KEYWORD", "STRING_CONST"]: # todo STRING_CONST might not needed
            self.compile_term()  # Compile the first term for number or var or function or string or [true, false,this]

        while (self.token_generator.token_type() == "SYMBOL" and (self.token_generator.symbol()
               in arithmetic_vm_symbol_table or self.token_generator.symbol() =='(')):  # it's Symbol meaning operator
            op = self.token_generator.symbol()
            if op == '(':
                self.token_generator.advance()  # '('
                self.compile_expression()
                self.token_generator.advance()  # ')'
            else:
                vm_op = arithmetic_vm_symbol_table[op]
                self.token_generator.advance()
                self.compile_expression()
                # self.token_generator.advance()


                if op in ["+", "-", "&", "|", "<", ">", "=", "^", "#", "~"]:  # regular arithmetics
                    self.writer.write_arithmetic(vm_op)
                elif op == "*":
                    self.writer.write_call('Math.multiply', 2)
                else:  # it's "/"
                    self.writer.write_call('Math.divide', 2)

    def compile_term(self):
        token_type = self.token_generator.token_type()
        if token_type == "INT_CONST":
            self.writer.write_push("CONST", self.token_generator.int_val())
            self.token_generator.advance()  # past expression
        elif token_type == "STRING_CONST":
            string_val = self.token_generator.string_val()
            self.writer.write_push("CONST", len(string_val))
            self.writer.write_call("String.new", 1)
            for char in string_val:
                self.writer.write_push("CONST", ord(char))
                self.writer.write_call("String.appendChar", 2)
            self.token_generator.advance()  # past expression
        elif token_type == "KEYWORD":  # true, false, null, this
            keyword_constant = self.token_generator.keyword()
            self._compile_keyword_constant(keyword_constant)
            self.token_generator.advance()  # past expression
        elif token_type == "IDENTIFIER":
            var_name = self.token_generator.identifier()
            self.token_generator.advance()  # for var past expression
            if self.token_generator.symbol() in ["[", "(", "."]:  # it's a function call
                self._compile_identifier_function_call(var_name)  # this will advance past expression
                #self.token_generator.advance()
            else:  # it's a regular var
                kind = self.symbol_table.kind_of(var_name)
                index = self.symbol_table.index_of(var_name)
                if kind is not None and index != -1:
                    segment = self._segment_of(kind)
                    self.writer.write_push(segment, index)

        elif self.token_generator.symbol() == "(":
            self.token_generator.advance()  # '('
            self.compile_expression()
            self.token_generator.advance()  # ')'
        elif self.token_generator.symbol() in ["-", "~", "^", "#"]:
            unary_op = self.token_generator.symbol()
            self.token_generator.advance()
            self.compile_term()
            self.writer.write_arithmetic(arithmetic_vm_symbol_table[unary_op])
            self.token_generator.advance()  # past expression

    def _compile_identifier_function_call(self, var_name):
        # This identifier could be an array entry, a subroutine call, or a class/static variable
        next_symbol = self.token_generator.symbol()

        if next_symbol == "[":  # it's an array
            # Array access, validate variable first
            kind = self.symbol_table.kind_of(var_name)
            index = self.symbol_table.index_of(var_name)
            if kind is not None and index != -1:
                self.writer.write_push(self._segment_of(kind), index)
                self.token_generator.advance()  # Advance to expression
                self.compile_expression()  # Compute the array index
                # self.token_generator.advance()  # past expression
                self.writer.write_arithmetic("ADD")  # Add the base address and the index
                self.writer.write_pop("POINTER", 1)  # Set THAT to the array element
                self.writer.write_push("THAT", 0)  # Push the value of the array element onto the stack
                self.token_generator.advance()  # Advance past ']'
        elif next_symbol in ["(", "."]:
            # Proceed with subroutine call or class/static variable; validation inside _compile_subroutine_call
            self._compile_subroutine_call(var_name)
        else:
            # Simple variable, ensure it's valid before proceeding
            kind = self.symbol_table.kind_of(var_name)
            index = self.symbol_table.index_of(var_name)
            if kind is not None and index != -1:
                segment = self._segment_of(kind)
                self.writer.write_push(segment, index)


    def _compile_subroutine_call(self, name):
        # Compile a subroutine call
        nArgs = 0

        if self.token_generator.symbol() == ".":
            # It's a class/var name followed by a '.', so capture the subroutine name
            self.token_generator.advance()  # Advance to subroutineName
            subroutine_name = self.token_generator.identifier()
            
            kind = self.symbol_table.kind_of(name)
            if kind:  # It's a variable, thus an object method call
                index = self.symbol_table.index_of(name)

                self.writer.write_push(self._segment_of(kind), index)
                nArgs += 1  # The object is the first argument
                class_name = self.symbol_table.type_of(name)  # the class type
                name = class_name #f"{class_name}.{subroutine_name}"
            # else:  # It's a class, so a function call or a constructor
            name = f"{name}.{subroutine_name}"
                
            self.token_generator.advance()  # Advance to '('

        elif self.token_generator.symbol() == "(":
            # It's a subroutine in the same class; we implicitly use 'this'
            self.writer.write_push("POINTER", 0)
            nArgs += 1
            name = f"{self.class_name}.{name}"  # function called is in this class


        # '(' should already be consumed here actually, so this might need adjusting
        # Check if next token is not '(', then advance, otherwise compile_expression_list will handle it
        # if self.token_generator.symbol() != "(":
        #     self.token_generator.advance()
        self.token_generator.advance()  # past '('
        nArgs += self.compile_expression_list()  # Compile the list of expressions
        self.token_generator.advance()  # past ')'
        self.writer.write_call(name, nArgs)
        


    def _compile_keyword_constant(self, keyword_constant):
        # Handle keyword constants true, false, null, this
        if keyword_constant == "TRUE":
            self.writer.write_push("CONST", 1)
            self.writer.write_arithmetic("neg")  # In VM, true is -1
        elif keyword_constant == "FALSE" or keyword_constant == "NULL":
            self.writer.write_push("CONST", 0)  # False and null are 0 in VM
        elif keyword_constant == "THIS":
            self.writer.write_push("POINTER", 0)  # Push the base address of the current object

    def compile_expression_list(self) -> int:
        counter = 0  # Reset at the start of compiling an expression list
        #self.token_generator.advance()
        if not self.token_generator.symbol() == ")":  # Check for non-empty list
            # NOTE: at this point '1' is the current token
            self.compile_expression()  # compile_expression will advance token_generator correctly
            # self.token_generator.advance()  # skip expression
            counter += 1
            while self.token_generator.symbol() == ",":
                self.token_generator.advance()  # Advance past ','
                self.compile_expression()  # compile_expression will advance token_generator correctly
                # self.token_generator.advance()  # skip expression
                counter += 1
        return counter
        # No additional advance needed here; the calling context will handle the closing ')'
