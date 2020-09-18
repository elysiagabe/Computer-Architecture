"""CPU functionality."""

import sys

# branch table key values
HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010 
ADD = 0b10100000
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110
# bitwise
AND = 0b10101000
OR = 0b10101010
XOR = 0b10101011
NOT = 0b01101001
SHL = 0b10101100
SHR = 0b10101101
MOD = 0b10100100

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.SP = 7
        self.FL = 0b00000000
        self.running = False
        # branch table
        self.branchtable = {}
        self.branchtable[HLT] = self.handle_HLT
        self.branchtable[LDI] = self.handle_LDI
        self.branchtable[PRN] = self.handle_PRN
        self.branchtable[MUL] = self.handle_MUL
        self.branchtable[ADD] = self.handle_ADD
        self.branchtable[PUSH] = self.handle_PUSH
        self.branchtable[POP] = self.handle_POP
        self.branchtable[CALL] = self.handle_CALL
        self.branchtable[RET] = self.handle_RET
        self.branchtable[CMP] = self.handle_CMP
        self.branchtable[JMP] = self.handle_JMP
        self.branchtable[JEQ] = self.handle_JEQ
        self.branchtable[JNE] = self.handle_JNE
        # bitwise
        self.branchtable[AND] = self.handle_AND
        self.branchtable[OR] = self.handle_OR
        self.branchtable[XOR] = self.handle_XOR
        self.branchtable[NOT] = self.handle_NOT
        self.branchtable[SHL] = self.handle_SHL
        self.branchtable[SHR] = self.handle_SHR
        self.branchtable[MOD] = self.handle_MOD

    def load(self):
        """Load a program into memory."""
        # Needs 2 file names (comp.py & program file name)...if not, print error
        if len(sys.argv) != 2: 
            print("usage: comp.py filename")
            sys.exit(1)
        
        try: 
            address = 0

            with open(sys.argv[1]) as f: 
                # sanitize data from file
                for line in f:
                    t = line.split('#')
                    n = t[0].strip()

                    if n == '':
                        continue

                    try:
                        n = int(n, 2)
                    except ValueError:
                        print(f"Invalid number: {n}")
                        sys.exit(1)

                    # commit program data to memory
                    self.ram[address] = n 
                    address += 1
        
        # If program file name not found/valid, print error
        except FileNotFoundError: 
            print(f"File not found: {sys.argv[1]}")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP": 
            # if a < b, set L flag to 1; otherwise set to 0
            if self.reg[reg_a] < self.reg[reg_b]: 
                self.FL = 0b00000100
            # if a > b, set G flag to 1; otherwise set to 0
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.FL = 0b00000010
            # if a = b, set E flag to 1; otherwise set to 0
            elif self.reg[reg_a] == self.reg[reg_b]:
                self.FL = 0b00000001
        # ~~~ BITWISE START ~~~ #
        elif op == "AND":
            self.reg[reg_a] = self.reg[reg_a] & self.reg[reg_b]
        elif op == "OR":
            self.reg[reg_a] = self.reg[reg_a] | self.reg[reg_b]
        elif op == "XOR":
            self.reg[reg_a] = self.reg[reg_a] ^ self.reg[reg_b]
        elif op == "NOT":
            self.reg[reg_a] = ~self.reg[reg_a]
        elif op == "SHL":
            self.reg[reg_a] = self.reg[reg_a] << self.reg[reg_b]
        elif op == "SHR":
            self.reg[reg_a] = self.reg[reg_a] >> self.reg[reg_b]
        elif op == "MOD":
            self.reg[reg_a] = self.reg[reg_a] % self.reg[reg_b]
        # ~~~ BITWISE END ~~~ #
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()
    
    # MAR = memory address register <-- address being read
    def ram_read(self, MAR): 
        MDR = self.ram[MAR]
        return MDR

    # MAR <-- address being written tO; MDR = memory data register <-- data being written to address
    def ram_write(self, MAR, MDR): 
        self.ram[MAR] = MDR 

    # push helper function
    def push_value(self, value): 
        self.reg[self.SP] -= 1
        self.ram[self.reg[self.SP]] = value

    # pop helper function
    def pop_value(self):
        value = self.ram[self.reg[self.SP]]
        self.reg[self.SP] += 1
        return value

    # HLT INSTRUCTION: Halt CPU & exit emulator
    def handle_HLT(self, a, b):
        self.running = False

    # LDI INSTRUCTION: Set value of register to an integer
    def handle_LDI(self, op_a, op_b): 
        self.reg[op_a] = op_b

    # PRN INSTRUCTION: print numeric value stored in given register
    def handle_PRN(self, op_a, b):
        print(f"{self.reg[op_a]}")

    # ~~~ ALU OPS START ~~~ #
    # MUL INSTRUCITON: Multiply values in 2 registers together & store result in registerA
    def handle_MUL(self, op_a, op_b):
        self.alu("MUL", op_a, op_b)
    
    def handle_ADD(self, op_a, op_b):
        self.alu("ADD", op_a, op_b)

    # CMP INSTRUCTION: Compare values in 2 registers & set flag value accordingly...handled by ALU
    def handle_CMP(self, op_a, op_b): 
        self.alu("CMP", op_a, op_b)

    def handle_AND(self, op_a, op_b):
        self.alu("AND", op_a, op_b)

    def handle_OR(self, op_a, op_b):
        self.alu("OR", op_a, op_b)

    def handle_XOR(self, op_a, op_b):
        self.alu("XOR", op_a, op_b)
    
    def handle_NOT(self, op_a, op_b):
        self.alu("NOT", op_a, op_b)
    
    def handle_SHL(self, op_a, op_b):
        self.alu("SHL", op_a, op_b)

    def handle_SHR(self, op_a, op_b):
        self.alu("SHR", op_a, op_b)

    def handle_MOD(self, op_a, op_b):
        self.alu("MOD", op_a, op_b)
    # ~~~ ALU OPS END ~~~ #

    # PUSH INSTRUCTION: Push the value in the given register on the stack
    def handle_PUSH(self, op_a, b):
        # get value to push...operand_a is reg num to push 
        value = self.reg[op_a]

        # call push helper function (decrements SP & copies value to SP addr)
        self.push_value(value)
    
    # POP INSTRUCTION: Pop the value at the top of the stack into the given register
    def handle_POP(self, op_a, b): 
        # get value at top of stack address w/ pop helper function (this also increments SP)
        value = self.pop_value()

        # store value in the register (reg num to pop into is operand_a)
        self.reg[op_a] = value

    # CALL INSTRUCTION: Calls a subroutine at the address stored in the register
    def handle_CALL(self, a, b):
        # compute the return address...call has 1 operand (pc+1), so this will be pc+2
        return_addr = self.pc + 2 
        # push return addr on stack
        self.push_value(return_addr)
        # get the value from the operand reg
        value = self.reg[self.ram[self.pc+1]]
        # set the pc to that value (addr of subroutine)
        self.pc = value

    # RET INSTRUCTION: Return from subroutine...pop the value from the top of the stack & store it in the PC
    def handle_RET(self, a, b): 
        # pop value from top of stack
        value = self.pop_value()
        # # set pc to that value (return addr)
        self.pc = value

    # ~~~ JUMPS ~~~ #
    # JMP INSTRUCTION: Jump to the address stored in the given register; set PC to addr stored in given reg
    def handle_JMP(self, op_a, b): 
        self.pc = self.reg[op_a]

    # JEQ INSTRUCTION: if equal flag is set (True, 1), jump to address stored in given reg...otherwise go to next? 
    def handle_JEQ(self, op_a, b): 
        if self.FL == 0b00000001: 
            self.pc = self.reg[op_a]
        else: 
            self.pc += 2
    
    # JNE INSTRUCTION: If E flag is clear (false, 0), jump to the address stored in the given register
    def handle_JNE(self, op_a, b):
        if self.FL != 0b00000001: 
            self.pc = self.reg[op_a]
        else: 
            self.pc += 2
    # ~~~ JUMPS END ~~~ #

    def run(self):
        """Run the CPU."""
        # initialize stack pointer
        self.reg[self.SP] = 0xF4

        # set running to True
        self.running = True

        # Iterate thru
        while self.running: 
            # set instruction register
            ir = self.ram_read(self.pc)

            # find num of operands (use to dynamically set pc incrementation)
            operand_count = (ir & 0b11000000) >> 6
            increment_num = operand_count + 1

            op_a = self.ram_read(self.pc+1)
            op_b = self.ram_read(self.pc+2)

            # print(f"ir is {ir:>08b}")
            # check if instruction sets PC (e.g., CALL or RET)...4th bit 
            inst_sets_pc = (ir & 0b00010000) >> 4

            if ir in self.branchtable:

                # use branchtable to complete corresponding instruction
                self.branchtable[ir](op_a, op_b)

                # if it does not, increment pc based on # of operands
                if inst_sets_pc == 0: 
                    # increment pc
                    self.pc += increment_num
            
            else: 
                self.running = False
                print(f"Unknown instruction {ir:>08b}")
