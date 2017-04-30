#ZhangXinqian 2017/4/29 
import sys
import getopt

class MIPSSimulator(object):
    
    __begin_addr = 128
    __instr_len = 4
    
    __category1 = {
        "000" : lambda bin_instr: "J #%d" % (int(bin_instr[6:]+"00", 2)), 
        "010" : lambda bin_instr: "BEQ R%d, R%d, #%d" % (int(bin_instr[6:11], 2), 
                                                         int(bin_instr[11:16], 2), 
                                                         MIPSSimulator.__bin2dec(bin_instr[16:]+"00")), 
        "100" : lambda bin_instr: "BGTZ R%d, #%d" % (int(bin_instr[6:11], 2), 
                                                     MIPSSimulator.__bin2dec(bin_instr[16:]+"00")), 
        "101" : lambda bin_instr: "BREAK", 
        "110" : lambda bin_instr: "SW R%d, %d(R%d)" % (int(bin_instr[11:16], 2),
                                                       MIPSSimulator.__bin2dec(bin_instr[16:]),
                                                       int(bin_instr[6:11], 2)), 
        "111" : lambda bin_instr: "LW R%d, %d(R%d)" % (int(bin_instr[11:16], 2),
                                                       MIPSSimulator.__bin2dec(bin_instr[16:]),
                                                       int(bin_instr[6:11], 2))
    }
    
    __category2 = {
        "000" : lambda bin_instr: "ADD R%d, R%d, R%d" % MIPSSimulator.__format_category2(bin_instr),
        "001" : lambda bin_instr: "SUB R%d, R%d, R%d" % MIPSSimulator.__format_category2(bin_instr), 
        "010" : lambda bin_instr: "MUL R%d, R%d, R%d" % MIPSSimulator.__format_category2(bin_instr), 
        "011" : lambda bin_instr: "AND R%d, R%d, R%d" % MIPSSimulator.__format_category2(bin_instr), 
        "100" : lambda bin_instr: "OR R%d, R%d, R%d" % MIPSSimulator.__format_category2(bin_instr), 
        "101" : lambda bin_instr: "XOR R%d, R%d, R%d" % MIPSSimulator.__format_category2(bin_instr), 
        "110" : lambda bin_instr: "NOR R%d, R%d, R%d" % MIPSSimulator.__format_category2(bin_instr)
    }
    
    __category3 = {
        "000" : lambda bin_instr: "ADDI R%d, R%d, #%d" % MIPSSimulator.__format_category3(bin_instr), 
        "001" : lambda bin_instr: "ANDI R%d, R%d, #%d" % MIPSSimulator.__format_category3(bin_instr), 
        "010" : lambda bin_instr: "ORI R%d, R%d, #%d" % MIPSSimulator.__format_category3(bin_instr), 
        "011" : lambda bin_instr: "XORI R%d, R%d, #%d" % MIPSSimulator.__format_category3(bin_instr)
    }
    
    __instrs = {
        "000" : lambda bin_instr: MIPSSimulator.__category1[bin_instr[3:6]](bin_instr), 
        "110" : lambda bin_instr: MIPSSimulator.__category2[bin_instr[13:16]](bin_instr),
        "111" : lambda bin_instr: MIPSSimulator.__category3[bin_instr[13:16]](bin_instr)
    }

    @staticmethod
    def __bin2dec(binary):
        if binary[0] == "0":
            return int(binary[1:], 2)
        else:
            s = ""
            for bit in binary[1:]:
                if bit == "0":
                    s += "1"
                else:
                    s += "0"
            return -(int(s, 2)+1)
 
    @staticmethod
    def __format_category2(bin_instr):
        return (int(bin_instr[16:21], 2), int(bin_instr[3:8], 2), int(bin_instr[8:13], 2))
    
    @staticmethod
    def __format_category3(bin_instr):
        return (int(bin_instr[8:13], 2), int(bin_instr[3:8], 2), MIPSSimulator.__bin2dec(bin_instr[16:])) 
    
    def __format_simulation_registers(self):
        output = "Registers\n"\
            "R00:\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\n"\
            "R08:\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\n"\
            "R16:\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\n"\
            "R24:\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\n\n" % tuple(self.__registers)
        return output
    
    def __format_simulation_data(self):
        output = "Data\n"
        addrs = range(self.__data_addr, self.__data_addr_end, self.__instr_len)
        i = 0
        while i < len(addrs)-1:
            alignment = []
            for addr in addrs[i:i+8]:
                alignment.append(self.__data[addr])            
            output += "%d:\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\n" % ((addrs[i],) + tuple(alignment))
            i += 8    
        output+="\n"
        return output

    def __format_simulation_queues(self):
        output = "IF Unit:\n"
        output += "\tWaiting Instruction:%s\n" % (self.__waiting_instr)
        output += "\tExecuted Instruction:%s\n" % (self.__executed_instr)
        output += "Pre-Issue Queue:\n"
        output += "Pre-ALU Queue:\n"
        output += "Pre-MEM Queue:\n"
        output += "Post-MEM Queue:\n"
        output += "Post-ALU Queue:\n"
        output+="\n"
        return output

    def __format_simulation_output(self, cycle):
        output = "--------------------\nCycle:%d\n\n" % (cycle)
        output += self.__format_simulation_queues()
        output += self.__format_simulation_registers()
        output += self.__format_simulation_data()
        return output
    
    __do_category2 = {
        "ADD" : lambda rs, rt : rs + rt,
        "SUB" : lambda rs, rt : rs - rt,
        "MUL" : lambda rs, rt : rs * rt,
        "AND" : lambda rs, rt : rs & rt,
        "OR" : lambda rs, rt : rs | rt,
        "XOR" : lambda rs, rt : rs ^ rt,
        "NOR" : lambda rs, rt : ~(rs | rt)
    }
    
    __do_category3 = {
        "ADDI" : lambda rs, immed: rs + immed,
        "ANDI" : lambda rs, immed: rs & immed,
        "ORI" : lambda rs, immed: rs | immed,
        "XORI" : lambda rs, immed: rs ^ immed
    }
    
    def __do_branch(self, instr_comp):
        res = True
        self.__is_stalled = False
        if instr_comp[0] == "J":
            self.__pc = int(instr_comp[1].replace("#", ""))
        elif instr_comp[0] == "BEQ":
            rsi = int(instr_comp[1].replace("R", ""))
            rti = int(instr_comp[2].replace("R", ""))
            if self.__locks[rsi] == 1 or self.__locks[rti] == 1:
                self.__is_stalled = True
                res = False
            elif self.__registers[rsi] == self.__registers[rti]:
                self.__pc += int(instr_comp[3].replace("#", ""))
        elif instr_comp[0] == "BGTZ":
            rsi = int(instr_comp[1].replace("R", ""))
            if self.__locks[rsi] == 1:
                self.__is_stalled = True
                res = False
            elif self.__registers[rsi] > 0:
                self.__pc += int(instr_comp[2].replace("#", ""))
        return res
    
    def __do_alu(self, instr_comp):
        regs = None
        res = None
        if instr_comp[0] in ("ADD", "SUB", "MUL", "AND", "OR", "XOR", "NOR"):
            rdi = int(instr_comp[1].replace("R", ""))
            rsi = int(instr_comp[2].replace("R", ""))
            rti = int(instr_comp[3].replace("R", ""))
            regs = (rdi, rsi, rti)
            res = MIPSSimulator.__do_category2[instr_comp[0]](self.__registers[rsi], self.__registers[rti])
        elif instr_comp[0] in ("ADDI", "ANDI", "ORI", "XORI"):
            rti = int(instr_comp[1].replace("R", ""))
            rsi = int(instr_comp[2].replace("R", ""))
            immed = int(instr_comp[3].replace("#", ""))
            regs = (rti, rsi)
            res = MIPSSimulator.__do_category3[instr_comp[0]](self.__registers[rsi], immed)
        return regs, res

    def __do_mem(self, instr_comp):
        reg = None
        res = None
        if instr_comp[0] in ("SW", "LW"):
            rti = int(instr_comp[1].replace("R", ""))
            [offset, base] = instr_comp[2].split("(")
            offset = int(offset)
            base = self.__registers[int(base.replace("R", "").replace(")", ""))]
            if instr_comp[0] == "SW":
                self.__data[base+offset] = self.__registers[rti]
            elif instr_comp[0] == "LW":
                reg = rti
                res = self.__data[base+offset]
        return reg, res

    def __can_issue(self, instr):
        return True

    def __IF(self):
        out = []
        self.__executed_instr = ""
        if self.__is_stalled:
            instr_comp = self.__waiting_instr.replace(",", "").split(" ")
            if self.__do_branch(instr_comp):
                self.__executed_instr = self.__waiting_instr
                self.__waiting_instr = ""
        else:
            fetch_count = 2
            while not self.__is_break and fetch_count > 0 and len(self.__pre_issue) < 4:
                instr = self.__assembly_code[self.__pc]
                self.__pc += self.__instr_len    
                instr_comp = instr.replace(",", "").split(" ")
                if instr_comp[0] == "BREAK":
                    self.__is_break = True
                elif instr_comp[0] in ("J", "BEQ", "BGTZ"):
                    if self.__do_branch(instr_comp):
                        self.__executed_instr = instr
                    else:
                        self.__waiting_instr = instr
                    break
                else:
                    out.append(instr)                     
                    fetch_count -= 1
        return out
    
    def __issue(self):
        out = []
        has_issued = 0
        for instr in self.__pre_issue:
            if len(self.__pre_alu)+has_issued == 2:
                break
            if self.__can_issue(instr):
                out.append(instr)
                has_issued += 1        
        return out
    
    def __alu(self):
        pre_mem_out = []
        post_alu_out = []
        if len(self.__pre_alu) > 0:
            instr = self.__pre_alu.pop(0)
            instr_comp = instr.replace(",", "").split(" ")
            if instr_comp[0] in ("SW", "LW"):      
                pre_mem_out.append(instr)
            else:
                regs, res = self.__do_alu(instr_comp)
                post_alu_out.append((instr, regs, res))
        return post_alu_out, pre_mem_out
    
    def __mem(self):
        out = []
        if len(self.__pre_mem) == 1:
            instr = self.__pre_mem.pop(0)
            instr_comp = instr.replace(",", "").split(" ")
            reg, res = self.__do_mem(instr_comp)
            if reg != None and res != None:
                out.append((instr, reg, res))
        return out
    
    def __wb(self):
        if len(self.__post_alu) == 1:
            buff = self.__post_alu.pop(0)
            self.__registers[buff[1][0]] = buff[2]
        if len(self.__post_mem) == 1:
            buff = self.__post_mem.pop(0)
            self.__registers[buff[1]] = buff[2]
    
    def disassemble(self, binary_path):
        try:
            binary_file = open(binary_path, "r")
        except:
            print "[!!!] Can't not open binary file."
            sys.exit(1)          
        try:
            binary = binary_file.read()
        except:
            print "[!!!] Can't not read binary file."
            sys.exit(1)
        finally:
            binary_file.close()
        iscode = True
        addr = self.__begin_addr        
        disassembly = ""
        self.__assembly_code = {}
        self.__data = {}
        for bin_instr in binary.split("\n"):
            if iscode:
                instr = self.__instrs[bin_instr[0:3]](bin_instr)
                disassembly += "%s\t%d\t%s\n" % (bin_instr, addr, instr)
                self.__assembly_code[addr] = instr
                if instr == "BREAK":
                    iscode = False
                    self.__data_addr = addr + self.__instr_len
            else:
                data = self.__bin2dec(bin_instr)
                disassembly += "%s\t%d\t%d\n" % (bin_instr, addr, data)
                self.__data[addr] = data
            addr += self.__instr_len
        self.__data_addr_end = addr
        return disassembly
    
    def simulate(self, binary_path):
        self.disassemble(binary_path)
        self.__pc = self.__begin_addr
        cycle = 1
        self.__registers = [
            0, 0, 0, 0, 0, 0, 0, 0, 
            0, 0, 0, 0, 0, 0, 0, 0, 
            0, 0, 0, 0, 0, 0, 0, 0, 
            0, 0, 0, 0, 0, 0, 0, 0
        ]
        self.__locks = [
            0, 0, 0, 0, 0, 0, 0, 0, 
            0, 0, 0, 0, 0, 0, 0, 0, 
            0, 0, 0, 0, 0, 0, 0, 0, 
            0, 0, 0, 0, 0, 0, 0, 0
        ]
        self.__waiting_instr = ""
        self.__executed_instr = ""
        self.__pre_issue = []
        self.__pre_alu = []
        self.__post_alu = []
        self.__pre_mem = []
        self.__post_mem = []
        simulation = ""
        self.__is_break = False
        self.__is_stalled = False
        while True:
            instr = self.__assembly_code[self.__pc]
            self.__pre_issue.extend(self.__IF())
            self.__pre_alu.extend(self.__issue())
            post_alu_out, pre_mem_out = self.__alu()
            self.__post_alu.extend(post_alu_out)
            self.__pre_mem.extend(pre_mem_out)
            self.__post_mem.extend(self.__mem())
            self.__wb()
            simulation += self.__format_simulation_output(cycle)
            cycle += 1
            if self.__is_break:
                break
        return simulation
    
    def write2file(self, output, file_path):
        try:
            f = open(file_path, "w")
        except:
            print "[!!!] Can't not open file."
            sys.exit(1)          
        try:
            f.write(output)
        except:
            print "[!!!] Can't not write file."
            sys.exit(1)
        finally:
            f.close()    

def usage():
    print "Usage: "
    print "-h                              - help"
    print "--help                          - help"
    print "-b binary_file                  - input binary to run"
    print "--binary=binary_file            - input binary to run"
    print "-d                              - disassemble and print to screen"
    print "--disassemble=disassembly_file  - disassemble and output disassembly to file"
    print "-s                              - simulate and print to screen"
    print "--simulate=simulation_file      - simulate and output simulation to file"
    print "Examples: "
    print "python MIPSsim.py -b sample.txt -d"
    print "python MIPSsim.py --binary=sample.txt --disassemble=disassembly.txt"
    print "python MIPSsim.py -b sample.txt --simulate=simulation.txt"
    print "python MIPSsim.py -b sample.txt -d -s"
    sys.exit(0)

if __name__ == '__main__':
    if not len(sys.argv[1:]):
        usage()
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hb:ds", ["help", "binary=", "disassemble=", "simulate="])
    except getopt.GetoptError as err:
        print str(err)
        usage()
    binary_file = ""
    disassembly_file = ""
    d = False
    simulation_file = ""
    s = False
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-b", "--binary"):
            binary_file = a
        elif o in ("-d", "--disassemble"):
            disassembly_file = a
            d = True
        elif o in ("-s", "--simulate"):
            simulation_file = a
            s = True
        else:
            assert False, "Unhandled Option."
    mipssim = MIPSSimulator()
    if binary_file != "":
        if d:
            disassembly = mipssim.disassemble(binary_file)
            if disassembly_file != "":
                mipssim.write2file(disassembly, disassembly_file)
            else:
                print disassembly
        if s:
            simulation = mipssim.simulate(binary_file)
            if simulation_file != "":
                mipssim.write2file(simulation, simulation_file)
            else:
                print simulation
        if not d and not s:
            print "No action to perform. Exit."
    else:
        print "No input binary file. Exit."