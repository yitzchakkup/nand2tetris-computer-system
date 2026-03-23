// This file is part of nand2tetris, as taught in The Hebrew University, and
// was written by Aviv Yaish. It is an extension to the specifications given
// [here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
// as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
// Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

// The program should swap between the max. and min. elements of an array.
// Assumptions:
// - The array's start address is stored in R14, and R15 contains its length
// - Each array value x is between -16384 < x < 16384
// - The address in R14 is at least >= 2048
// - R14 + R15 <= 16383
//
// Requirements:
// - Changing R14, R15 is not allowed.

// Put your code here.
@R14
D=M
@maxpointer
M=D // maxpointer initialized to *R14
@minpointer
M=D // minpointer initialized to *R14

@i
M=D
@R15
D = D+M
@endlist
M=D

(LOOP)
    @i
    D=M
    @endlist
    D=M-D//elemnts left to check
    @DONE
    D;JEQ //vent over entire list

    
    @i
    M=M+1//next element
    A=M
    D=M //value in new element
    @cur
    M=D
    @maxpointer
    A=M
    D=M
    @cur
    D=D-M//new element -*maxpointer
    @SKIPMAX 
    D;JGT// new element is smaller

    //else chnge maxpointer
    @i
    D=M
    @maxpointer
    M=D

    (SKIPMAX)
    @minpointer
    A=M
    D=M
    @cur
    D=D-M//new element -*minpointer
    @SKIPMIN
    D;JLT// new element is smaller


//else change min pointer 
    @i
    D=M
    @minpointer
    M=D

    (SKIPMIN)
    @LOOP
    0;JMP



    
(DONE)//swop
@maxpointer
D=M
A=D//A pointing to max element of array
D=M // D is max value
@i
M=D//*i=max value
@minpointer
D=M//D=*minpointer
A=M//A pointing to min element of array
D=M//D is min value
@maxpointer
A=M
M=D// *maxpointer = max value
@i
D=M// M is min value
@minpointer
A=M
M=D// *minpointer = min value



(END)
    @END 
    0;JMP