import extract_msg
import hashlib
import os
from datetime import dataetime
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class MessageInfo:
    filepath: str
    file_hash: str
    subject: str
    date: Optional[dataetime]
    body_hash: str
    message_id: Optional[str]
    in_replay_to: Optional[str]
    references: Optional[List[str]]

#Helper function used to clean the subject of prefixes such as RE:, FWD:, etc
def clean_subject(subject):
    
    subject_lower = subject.lower()

    subject_prefixes = ["re: ", "fwd: "]

    for prefix in subject_prefixes: 
        subject_lower = subject_lower.replace(prefix, '')
    
    return subject_lower

#parsing the information in a given msg file
def extract_msg_info(filepath):

    #verify that the file path leads to a .msg file
    _, ext = os.path.splitext(filepath)

    if ext.lower() != ".msg": 
        return None

    #first try to successfully run this code
    try: 
        
        #loading the message file
        msg = extract_msg.Message(filepath)  

        #temporarily open the passed file, create a hash with the binary data
        with open(filepath, 'rb') as f: 
            file_content = f.read()
            file_hash = hashlib.sha256(file_content).hexdigest()

        body = msg.body or ""                                           #save the body of the email, or if nothing make blank
        body_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()    #convert the body into bytes to create hash

        msg.subject = clean_subject(msg.subject)                        #clean the subject of the email

        

        return msg
    
    #if an error occurs, we print it to the console
    except Exception as e:
        print(f"An error occured while parsing{filepath} : {e}")
        return None