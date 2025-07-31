import msg_parser
import os
from models import MessageInfo
from typing import List, Dict

def collect_all_msg_info(directory_path: str) -> List[MessageInfo]:

    all_messages = []

    for filename in os.listdir(directory_path): 
        root, extension = os.path.splitext(filename)

        if filename.endswith(".msg"): 
            file_path = os.path.join(directory_path, filename)
            all_messages.append(msg_parser.extract_msg_info(file_path))

    return all_messages

def find_exact_file_duplicates(all_messages: List[MessageInfo]):
    
    dict_exact_duplicates = dict()

    #iterate through each exisiting file in the given directory
    for Message in all_messages:
        
        dict_exact_duplicates.setdefault(Message.file_hash, []).append(Message.filepath)
        print(Message.filepath)

    return dict_exact_duplicates
        
def find_thread_duplicates(all_messages: List[MessageInfo]):

    

    return None

#test code to run only if initating in this module
if __name__ == "__main__":
    
    foo = collect_all_msg_info("/home/jordan/msg_deduplicator/data")
    
    print(find_exact_file_duplicates(foo))