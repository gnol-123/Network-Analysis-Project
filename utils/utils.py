import json, os
from pathlib import Path

def load(inpJson):

    # load Json file
    try:
        with open(inpJson) as j:
            data = json.load(j)
            return data
        
    except FileNotFoundError:
        print("Couldnt find file")
        return -1
    except json.JSONDecodeError:
        print("Error decoding raw data json file")
        return -1
    
def dump(file, outPath):

    parent = Path(outPath).parent

    os.makedirs(parent, exist_ok=True)
    # dump
    try:
        with open(outPath, 'w', encoding='utf-8') as f:
            json.dump(file, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Failed dump: {e}")