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

def find_exact_file_duplicates(all_messages: List[MessageInfo]) -> Dict[str, List[str]]:
    
    dict_exact_duplicates = dict()

    #iterate through each exisiting file in the given directory
    for Message in all_messages:
        
        dict_exact_duplicates.setdefault(Message.file_hash, []).append(Message.filepath)

    return dict_exact_duplicates

def find_message_id_duplicates(all_messages: List[MessageInfo]) -> Dict[str, List[str]]:

    dict_message_id_duplicates = dict()

    for Message in all_messages: 
        dict_message_id_duplicates.setdefault(Message.message_id, []).append(Message.filepath)

    return dict_message_id_duplicates


def find_thread_duplicates(all_messages: List[MessageInfo]):

    #creating a dictionary of all messages with the message.id being the key
    dict_all_messages = {message.message_id : message for message in all_messages}

    parent_map = {}         #dictionary to map each email's parent email in the thread chain
    all_thread_ids = set()  #set to track list of unique message ids

    for key, value in dict_all_messages.items():
        print(key)

    for message_id, message in dict_all_messages.items(): 

        print("----")
        print(message_id)
        print(message.in_reply_to)
        print("----")

        #if the message has an in reply to that means it has a parent, store the parent id
        if message.in_reply_to: 
            parent_id = message.in_reply_to

            print("parent id: " + parent_id)
            print(parent_id in dict_all_messages)

            #if the parent_id is in the dict_all_messages then we can add the parent child relationship to the parent map
            #key -> child id : value -> parent id
            if parent_id in dict_all_messages:
                print("Entered")
                parent_map[message_id] = parent_id

                all_thread_ids.add(message_id)
                all_thread_ids.add(parent_id)

    #helper function used to walk to the root email of a thread
    def find_root(node_id): 
        while node_id in parent_map: 
            node_id = parent_map[node_id]
        return node_id
    
    #dict containing the root email id as the key and all children within a list as the value
    threads_by_root = {}

    #loop through all message ids in all_thread_ids
    for message_id in all_thread_ids: 

        root_id = find_root(message_id)                                                 #use find_root to get the root of the current message
        threads_by_root.setdefault(root_id, []).append(dict_all_messages[message_id])   #populate the threads by root dict using the cur message root


#test code to run only if initating in this module
if __name__ == "__main__":
    
    foo = collect_all_msg_info("/home/jordan/msg_deduplicator/data")
    
    """
    print("-------------------")
    print(find_exact_file_duplicates(foo))
    print("-------------------")
    print(find_message_id_duplicates(foo))
    print("-------------------")
    """

    find_thread_duplicates(foo)