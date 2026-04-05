'''
This module contains utility functions for blockchain.
'''

import os
import json
import hashlib
import time


def initialize_data_capture(path="captured_data.json"):
    # Create file to store captured data
    with open(path, "w") as f:
        json.dump({}, f)


def hash_json(filename):
    with open(filename, "r") as f:
        data = json.load(f)
    json_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(json_str.encode('utf-8')).hexdigest()


def hash_file(filepath, chunk_size=4194304):
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while True:
            # Read a chunk of the file
            chunk = f.read(chunk_size)
            if not chunk:
                # End of file reached
                break
            # Update the hash with the current chunk
            hasher.update(chunk)
    return hasher.hexdigest()


def hash_directory(directory, chunk_size=4194304):
    hasher = hashlib.sha256()
    for root, dirs, files in os.walk(directory):
        for file in sorted(files):  # Sort to ensure consistent order
            file_path = os.path.join(root, file)
            with open(file_path, "rb") as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    hasher.update(chunk)
    return hasher.hexdigest()


def create_dummy_json(data, path="dummy_data.json"):
    with open(path, "w") as f:
        json.dump(data, f)
        
        
def copy_file(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    os.system(f"cp {src} {dst}")


def create_filename(base_name, extension="json"):
    return f"{base_name}_{int(time.time())}_{hashlib.sha256(str(time.time()).encode('utf-8')).hexdigest()[:8]}.{extension}"


# capture the data to be saved in the blockchain
def capture_data(data_type, data, path="captured_data.json"):
    with open(path, "r") as f:
        metadata = json.load(f)
        
    if data_type == "json":
        # Update the metadata with the new data
        metadata[data_type].update(data) if data_type in metadata else metadata.update({data_type: data})
    elif data_type == "weights":
        # For files, the file is hashed
        file_hash = hash_file(data)
        metadata[data_type] = str(file_hash)
    elif data_type == "training_data":
        data_hash = hash_directory(data)
        metadata[data_type] = str(data_hash)
    else:
        raise ValueError("Unsupported data type for capture. Use 'json' or 'file'.")
            
    with open(path, "w") as f:
        json.dump(metadata, f, indent=4)
        

def get_captured_data(path="captured_data.json"):
    with open(path, "r") as f:
        return json.load(f)


def verify_captured_data(data_type, data, metadata):
    if data_type == "weights":
        file_hash = hash_file(data)
    elif data_type == "training_data":
        file_hash = hash_directory(data)
    else:
        print("Unsupported data type for verification. Use 'weights' for file verification.")
    
    if data_type in metadata and metadata[data_type] == file_hash:
        print("==============================================")
        print(f"Data integrity verified for {data_type}!")
        print("==============================================")
        return True
    
    print(f"Data integrity verification failed for {data_type}!")
    print(f"Expected hash: {metadata.get(data_type)}, Actual hash: {file_hash}")
    return False
    
    