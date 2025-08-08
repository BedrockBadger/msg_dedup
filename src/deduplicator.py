import msg_parser
import os
import re
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

def normalize_text(text: str) -> str: 

    if not text: 
        return ""
    
    text = re.sub(r'^>+\s?', '', text, flags=re.MULTILINE) #getting ride of characters >> or > at the start of new lines
    normailzed = re.sub(r'\s+', '', text)                  #removing all white spaces in the body - need for string comparision

    return normailzed

def find_thread_duplicates(all_messages: List[MessageInfo]):

    #creating a dictionary of all messages with the message.id being the key
    dict_all_messages = {message.message_id : message for message in all_messages}

    parent_map = {}         #dictionary to map each email's parent email in the thread chain
    all_thread_ids = set()  #set to track list of unique message ids

    for message_id, message in dict_all_messages.items(): 

        #if the message has an in reply to that means it has a parent, store the parent id
        if message.in_reply_to: 
            parent_id = message.in_reply_to

            #if the parent_id is in the dict_all_messages then we can add the parent child relationship to the parent map
            #key -> child id : value -> parent id
            if parent_id in dict_all_messages:
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

    #now create a dict using subject as the key, a list of messages that correspond to the key
    threads_by_subject = {}

    #populate the threads_by_subject with the threads that have already been grouped by their in-reply-to
    for threads_list in threads_by_root.values(): 
        thread_subject = threads_list[0].subject
        threads_by_subject.setdefault(thread_subject, []).extend(threads_list)

    thread_ids = set(threads_by_root.keys())
    for thread_list in threads_by_root.values(): 
        for message in thread_list: 
            thread_ids.add(message.message_id)

    unthreaded_messages = [message for message in all_messages if message.message_id not in thread_ids]

    for message in unthreaded_messages: 
        if message.subject in threads_by_subject: 
            threads_by_subject[message.subject].append(message)

    redundant_messages = []

    for root_id, thread in threads_by_subject.items(): 
        if len(thread) <= 1: 
            continue
        
        thread.sort(key = lambda msg: msg.date)

        for i in range(len(thread) - 1): 
            older_email = thread[i]
            newer_email = thread[i + 1]

            old_body = normalize_text(older_email.body)
            new_body = normalize_text(newer_email.body)

            #add as redundant if the thread message is a duplicate
            if older_email.body_hash == newer_email.body_hash: 
                redundant_messages.append(older_email)
            #add old message as a redundant if the new message contains all the content of the old message
            elif old_body in new_body: 
                redundant_messages.append(older_email)


        # Print the final grouped threads
    print("--- Final Grouped Threads ---")
    for subject, thread in threads_by_subject.items():
        print(f"Subject: '{subject}'")
        print(f"  Thread Size: {len(thread)}")
        for msg in thread:
            # Get the first line of the body for identification
            body_snippet = "No body content."
            if msg.body:
                words = msg.body.split()
                body_snippet = ' '.join(words[:10])
            print(f"    - Message ID: '{msg.message_id}', Date: {msg.date}, Snippet: '{body_snippet}'")
        print("-" * 30)

    # Print the list of redundant messages
    print("\n--- Redundant Messages Found ---")
    if not redundant_messages:
        print("No redundant messages found.")
    else:
        for msg in redundant_messages:
            # Get the first line of the body for identification
            body_snippet = "No body content."
            if msg.body:
                words = msg.body.split()
                body_snippet = ' '.join(words[:10])
            print(f"  - Message ID: '{msg.message_id}'")
            print(f"    Subject: '{msg.subject}'")
            print(f"    Date: {msg.date}")
            print(f"    Snippet: '{body_snippet}'")
            print("-" * 30)

    return redundant_messages


#test code to run only if initating in this module
if __name__ == "__main__":
    
    foo = collect_all_msg_info("/home/jordan/msg_deduplicator/data")
    
    """
    print("-------------------")
    print(find_exact_file_duplicates(foo))
    print("-------------------")
    print(find_message_id_duplicates(foo))
    print("-------------------")


    print("--- Verifying All Messages ---")
    for message_id, message in dict_all_messages.items():
        # Get the first line or a few words of the body for identification
        body_snippet = "No body content."
        if message.body:
            words = message.body.split()
            body_snippet = ' '.join(words[:10])  # Take the first 10 words
            
        print(f"Message ID: '{message_id}'")
        print(f"In-reply-to: '{message.in_reply_to}'")
        print(f"Body Snippet: '{body_snippet}'")
        print("------------------------------------------")

    for key, value in threads_by_root.items():
        # 'key' is the string ID of the thread's root email
        # 'value' is the list of MessageInfo objects in that thread

        print(f"--- Thread (Root ID: {key}) ---")

        # This inner loop is what you're missing.
        # It goes through each MessageInfo object in the list.
        for message in value:
            # Now you can access the attributes of each MessageInfo object.
            print(f"  - Subject: {message.subject}, Date: {message.date}")
    """

    find_thread_duplicates(foo)