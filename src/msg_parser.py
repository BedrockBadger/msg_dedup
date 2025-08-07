import extract_msg
import hashlib
import os
import re
from models import MessageInfo
from bs4 import BeautifulSoup

#Helper function used to clean the subject of prefixes such as RE:, FWD:, etc
def clean_subject(subject_string: str) -> str:
    
    if not subject_string: 
        return ""
    
    prefix_pattern = r"^(?:re|fw|fwd|aw):\s*"  

    cleaned_subject = subject_string

    while True: 
        new_subject = re.sub(prefix_pattern, "", cleaned_subject, flags=re.IGNORECASE)

        if cleaned_subject == new_subject: 
            break;
        cleaned_subject = new_subject.strip()

    return cleaned_subject.strip()

def clean_message_id(msg_id: str) -> str:

    #return empty string to handle null value
    if not msg_id: 
        return ''
    
    match = re.search(r'<(.*?)>', msg_id)   #search for pattern like < *content* > in msg_id

    #if a match was found, only return the match without the pointed brackets (group(1)) and remove leading or following white spaces .strip()
    if match:
        return match.group(1).strip()

    return msg_id.strip() #if no match is found remove whitespaces

# NOTE -> may move this into deduplicator and have the function only be called when needed rather than for every single parsed email
def normalize_text(text: str) -> str: 

    if not text: 
        return ""
    
    text = re.sub(r'^>+\s?', '', text, flags=re.MULTILINE) #getting ride of characters >> or > at the start of new lines
    normailzed = re.sub(r'\s+', '', text)                  #removing all white spaces in the body - need for string comparision

    return normailzed

#parsing the information in a given msg file
def extract_msg_info(filepath: str) -> MessageInfo:

    #verify that the file path leads to a .msg file
    _, ext = os.path.splitext(filepath)

    if ext.lower() != ".msg": 
        print("passed file was not a .msg file")
        return None

    #first try to successfully run this code
    try: 
        
        #loading the message file
        msg = extract_msg.Message(filepath)  

        #temporarily open the passed file, create a hash with the binary data
        with open(filepath, 'rb') as f: 
            file_content = f.read()
            file_hash = hashlib.sha256(file_content).hexdigest()

        email_body = msg.body or ""  #save the body of the email, or if nothing make blank
        
        #Try to get email body content from htmlBody if failed to retrieve from body
        if not email_body: 
            if msg.htmlBody: 
                soup = BeautifulSoup(msg.htmlBody, 'html.parser')
                email_body = soup.get_text()

        email_body = normalize_text(email_body)                               #use normalize helper on body text to allow for string comparision
        body_hash = hashlib.sha256(email_body.encode("utf-8")).hexdigest()    #convert the body into bytes to create hash

        msg.subject = clean_subject(msg.subject)                        #clean the subject of the email

        messageID = clean_message_id(msg.messageId)
        inReplyTo = clean_message_id(msg.inReplyTo)

        raw_reference_string = msg.header.get("References")
        reference_list = None

        if raw_reference_string: 
            parts = raw_reference_string.split()

            reference_list = [ref.strip() for ref in parts if ref.strip()]

        MessageData = MessageInfo(
            filepath = filepath,
            file_hash = file_hash,
            subject = msg.subject,
            sender = msg.sender,
            date = msg.date, 
            body_hash = body_hash, 
            body = email_body,
            message_id = messageID,
            in_reply_to = inReplyTo,
            references = reference_list
        )

        return MessageData
    
    #if an error occurs, we print it to the console
    except Exception as e:
        print(f"An error occured while parsing{filepath} : {e}")
        return None

#test code to run only if initating in this module
if __name__ == "__main__":
    messageObj = extract_msg_info('/home/jordan/msg_deduplicator/data/TestMessage.msg')
    messageObj.print_data()