from datetime import datetime
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class MessageInfo:
    filepath: str
    file_hash: str
    subject: str
    sender: str
    date: Optional[datetime]
    body_hash: str
    body: str
    message_id: Optional[str]
    in_reply_to: Optional[str]
    references: Optional[List[str]]

    def print_data(self):
        print("---------------------------")
        print(f"File path: {self.filepath}")
        print(f"File hash: {self.file_hash}")
        print(f"Subject: {self.subject}")
        print(f"Sender: {self.sender}")
        print(f"Date: {self.date.strftime('%Y-%m-%d %H:%M:%S') if self.date else 'N/A'}")
        print(f"Body_hash: {self.body_hash}")
        print(f"Message_id: {self.message_id if self.message_id else 'N/A'}")
        print(f"In reply to: {self.in_reply_to if self.in_reply_to else 'N/A'}")
        print(f"References: {','.join(self.references) if self.references else 'N/A'}")
        print("---------------------------")