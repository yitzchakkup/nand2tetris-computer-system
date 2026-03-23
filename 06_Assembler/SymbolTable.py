"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""


class SymbolTable:
    """
    A symbol table that keeps a correspondence between symbolic labels and 
    numeric addresses.
    """

    def __init__(self) -> None:
        """Creates a new symbol table initialized with all the predefined symbols
        and their pre-allocated RAM addresses, according to section 6.2.3 of the
        book.
        """
        symble_table = []
        for i in range(16):
            symble_table.append(("R"+str(i), i))

        symble_table.append(("SCREEN", 16384))
        symble_table.append(("KBD", 24576))

        symble_table.append(("SP", 0))
        symble_table.append(("LCL", 1))
        symble_table.append(("ARG", 2))
        symble_table.append(("THIS", 3))
        symble_table.append(("THAT", 4))
        self.symbel_table = symble_table

    def add_entry(self, symbol: str, address: int) -> None:
        """Adds the pair (symbol, address) to the table.

        Args:
            symbol (str): the symbol to add.
            address (int): the address corresponding to the symbol.
        """
        if not self.contains(symbol):
            self.symbel_table.append((symbol, address))

    def contains(self, symbol: str) -> bool:
        """Does the symbol table contain the given symbol?

        Args:
            symbol (str): a symbol.

        Returns:
            bool: True if the symbol is contained, False otherwise.
        """
        for my_symbol in self.symbel_table:
            if my_symbol[0] == symbol:
                return True
        return False

    def get_address(self, symbol: str) -> int:
        """Returns the address associated with the symbol.

        Args:
            symbol (str): a symbol.

        Returns:
            int: the address associated with the symbol.
        """
        for my_symbol in self.symbel_table:
            if my_symbol[0] == symbol:
                return my_symbol[1]
        return -1 #error symbole not in list, should't happen
