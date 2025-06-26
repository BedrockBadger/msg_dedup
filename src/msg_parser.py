import extract_msg

def extract_msg_info(filepath):

    msg = extract_msg.Message(filepath)  

    #msg.subject = clean_subject(msg.subject)
    print(msg.subject)

    return msg

def clean_subject(subject):
    
    subject_lower = subject.lower()

    subject_prefixes = ["re: ", "fwd: "]

    for prefix in subject_prefixes: 
        subject_lower = subject_lower.replace(prefix, '')
    
    return subject_lower


extract_msg_info("/home/jordan/msg_deduplicator/data/TestMessage.msg")