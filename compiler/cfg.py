class BasicBlock:
    def __init__(self, id_):
        self.id = id_
        self.instructions = []
        self.predecessors = []
        self.successors = []
        
    def add_instruction(self, instr):
        self.instructions.append(instr)
        
    def __repr__(self):
        return f"Block_{self.id}"

class CFG:
    def __init__(self, instructions):
        self.instructions = instructions
        self.blocks = []
        self.entry = None
        
    def build(self):
        if not self.instructions:
            return
            
        current_block = BasicBlock(0)
        self.blocks.append(current_block)
        self.entry = current_block
        
        block_id = 1
        label_to_block = {}
        
        # 1st Pass: Create blocks at Leaders (labels, after jumps)
        for instr in self.instructions:
            op = instr[0]
            if op == 'LABEL':
                new_block = BasicBlock(block_id)
                block_id += 1
                self.blocks.append(new_block)
                label_to_block[instr[1]] = new_block
                current_block = new_block
                current_block.add_instruction(instr)
            else:
                current_block.add_instruction(instr)
                if op in ('GOTO', 'IF_FALSE_GOTO', 'RETURN', 'RETURN_VOID'):
                    new_block = BasicBlock(block_id)
                    block_id += 1
                    self.blocks.append(new_block)
                    current_block = new_block
                    
        # 2nd Pass: Add edges
        for i, block in enumerate(self.blocks):
            if not block.instructions:
                continue
            last_instr = block.instructions[-1]
            op = last_instr[0]
            
            if op == 'GOTO':
                target = label_to_block.get(last_instr[1])
                if target:
                    block.successors.append(target)
                    target.predecessors.append(block)
            elif op == 'IF_FALSE_GOTO':
                target = label_to_block.get(last_instr[2])
                if target:
                    block.successors.append(target)
                    target.predecessors.append(block)
                # Fallthrough
                if i + 1 < len(self.blocks):
                    next_block = self.blocks[i+1]
                    block.successors.append(next_block)
                    next_block.predecessors.append(block)
            elif op not in ('RETURN', 'RETURN_VOID'):
                # Fallthrough
                if i + 1 < len(self.blocks):
                    next_block = self.blocks[i+1]
                    block.successors.append(next_block)
                    next_block.predecessors.append(block)

    def print_cfg(self):
        print("--- Control Flow Graph ---")
        for block in self.blocks:
            if not block.instructions: continue
            print(f"[{block.id}] Instructions: {len(block.instructions)}")
            print(f"    Successors: {[b.id for b in block.successors]}")
        print("--------------------------")
