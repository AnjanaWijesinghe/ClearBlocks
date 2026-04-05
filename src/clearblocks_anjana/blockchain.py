import hashlib
import json
import time
import os

from . import blockchain_utils as bc_utils


# The file where your blockchain will live permanently
CHAIN_DATA_FILE = "blockchain_state.json"

class Block:
    def __init__(self, index, previous_hash, timestamp, file_hash, file_name, block_hash):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.file_hash = file_hash  
        self.file_name = file_name  
        self.block_hash = block_hash

    # Helper to convert the block object into a dictionary for saving
    def to_dict(self):
        return {
            "index": self.index,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "file_hash": self.file_hash,
            "file_name": self.file_name,
            "block_hash": self.block_hash
        }
        
class Blockchain:
    def __init__(self):
        self.chain = []
        self.load_chain()  # Attempt to load existing data on startup
        
    def load_chain(self):
        # Check if there is an existing saved blockchain
        if os.path.exists(CHAIN_DATA_FILE):
            with open(CHAIN_DATA_FILE, 'r') as file:
                chain_data = json.load(file)
                for block_data in chain_data:
                    # Rebuild the Block objects from the saved dictionaries
                    block = Block(
                        block_data['index'], 
                        block_data['previous_hash'], 
                        block_data['timestamp'], 
                        block_data['file_hash'], 
                        block_data['file_name'], 
                        block_data['block_hash']
                    )
                    self.chain.append(block)
            print(f"Loaded existing blockchain with {len(self.chain)} blocks.")
        else:
            print("No existing blockchain found. Creating genesis block...")
            self.create_genesis_block()
            
            
    def save_chain(self):
        # Save the current state of the chain to a JSON file
        with open(CHAIN_DATA_FILE, 'w') as file:
            chain_data = [block.to_dict() for block in self.chain]
            json.dump(chain_data, file, indent=4)
            
            
    def create_genesis_block(self):
        genesis_block = self.mine_block(0, "0", time.time(), "Genesis Hash", "genesis")
        self.chain.append(genesis_block)
        self.save_chain()  # Save immediately after creation
        
        
    def calculate_block_hash(self, index, previous_hash, timestamp, file_hash):
        value = str(index) + str(previous_hash) + str(timestamp) + str(file_hash)
        return hashlib.sha256(value.encode('utf-8')).hexdigest()
    
    
    def mine_block(self, index, previous_hash, timestamp, file_hash, file_name):
        block_hash = self.calculate_block_hash(index, previous_hash, timestamp, file_hash)
        return Block(index, previous_hash, timestamp, file_hash, file_name, block_hash)
    
    
    def anchor_file_hash(self, file_hash, file_name):
        last_block = self.chain[-1]
        new_block = self.mine_block(
            index=last_block.index + 1,
            previous_hash=last_block.block_hash,
            timestamp=time.time(),
            file_hash=file_hash,
            file_name=file_name
        )
        self.chain.append(new_block)
        self.save_chain()  # Save the chain every time a new block is added
        print(f"--> Block #{new_block.index} added and saved! Anchored hash for '{file_name}'")
        
    
    def verify_file(self, file_hash, file_name):
        for block in self.chain:
            if block.file_hash == file_hash:
                return True, block.index
        return False, None
    

def initialize_blockchain():
    my_chain = Blockchain()
    

def create_blockchain_entry(file_name, anchor_store='anchored_files'):
    my_chain = Blockchain()  # Load existing chain or create new one
    
    file_hash = bc_utils.hash_json(file_name)
    file_base_name = os.path.basename(file_name)
    my_chain.anchor_file_hash(file_hash, file_base_name)
    
    # Store the anchored file
    bc_utils.copy_file(file_name, os.path.join(anchor_store, file_base_name))
    print(f"File '{file_base_name}' anchored with hash: {file_hash}")
    
    
def verify_blockchain_entry(file_name):
    my_chain = Blockchain()  
    
    file_hash = bc_utils.hash_json(file_name)
    is_valid, block_index = my_chain.verify_file(file_hash, file_name)
    
    if is_valid:
        print(f"File '{file_name}' is anchored in block #{block_index}. Verification successful!")
    else:
        print(f"File '{file_name}' is NOT anchored in the blockchain. Verification failed.")
        
    return is_valid, block_index
        
        
    
