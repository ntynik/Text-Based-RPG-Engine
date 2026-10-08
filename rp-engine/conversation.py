from dataclasses import dataclass, asdict
import json
import uuid
from config import VERSION

@dataclass
class Message:
    id: str
    role: str
    content: str
    parent_id: str | None

    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        return cls(
            id=data["id"],
            role=data["role"],
            content=data["content"],
            parent_id=data["parent_id"]
        )

@dataclass
class Branch:
    id: str
    head_message_id: str
    status: str
    
    @classmethod
    def from_dict(cls, data: dict) -> "Branch":
        return cls(
            id=data["id"],
            head_message_id=data["head_message_id"],
            status=data["status"]
        )

class Conversation:
    def __init__(self, system_prompt):
        message_id=str(uuid.uuid4())
        branch_id=str(uuid.uuid4())
        
        system_message=Message(
            message_id, 
            role="system", 
            content=system_prompt, 
            parent_id=None
            )
        
        self.messages = {
            message_id : system_message
            }
        
        self.branches={
            branch_id : Branch(branch_id, message_id, "active")
            }
        
        self.current_branch_id=branch_id
    
    def add_user_message(self, content: str) -> None:
        message_id=str(uuid.uuid4())
        current_branch=self.branches[self.current_branch_id]
        self.messages[message_id]=(Message(
            id=message_id, 
            role="user", 
            content=content, 
            parent_id=current_branch.head_message_id
            ))
        current_branch.head_message_id=message_id

    def add_assistant_message(self, content: str) -> None:
        message_id=str(uuid.uuid4())
        current_branch=self.branches[self.current_branch_id]
        self.messages[message_id]=(Message(
            id = message_id, 
            role = "assistant", 
            content = content, 
            parent_id=current_branch.head_message_id
            ))
        current_branch.head_message_id=message_id
    
    def get_provisional_messages(self, user_message: str | None = None, end_message_id: str | None = None) -> list[dict[str, str]]:
        provisional_messages=[]
        messages_to_keep = []
        
        if end_message_id is not None:
            messages_to_keep = self.get_message_path(self.messages[end_message_id].parent_id)
        else:
            messages_to_keep = self.get_active_path()

        for message_id in messages_to_keep:
            message=self.messages[message_id]
            provisional_messages.append({
                            "role" : message.role,
                            "content" : message.content
                        })
        
        if user_message is not None:
            provisional_messages.append({
                "role" : "user",
                "content" : user_message
                })
        
        return provisional_messages

    def get_message_path(self, message_id: str) -> list[str]:
        path = []
        current_id = message_id

        while current_id is not None:
            path.append(current_id)
            current_id = self.messages[current_id].parent_id

        path.reverse()
        return path

    def get_active_path(self) -> list[str]:
        head_message_id = self.branches[self.current_branch_id].head_message_id
        return self.get_message_path(head_message_id)

    def create_branch(self, message_id: str) -> str:
        if message_id not in self.messages:
            raise KeyError(f"Message {message_id} does not exist.")
        
        branch_id = str(uuid.uuid4())
        self.branches[branch_id] = Branch(id=branch_id, head_message_id=message_id, status="active")
        return branch_id

    def switch_branch(self, branch_id: str) -> None:
        if branch_id not in self.branches:
            raise KeyError(f"Branch {branch_id} does not exist.")

        if self.branches[branch_id].status != "active":
            raise ValueError(f"Branch {branch_id} is not active.")

        self.current_branch_id = branch_id

    def create_regeneration_branch(self) -> None:
        if self.messages[message_to_regen_id].role != "assistant":
            raise ValueError("Only assistant messages can be regenerated.")

        if self.messages[message_to_regen_id].parent_id is None:
            raise ValueError("The root message cannot be regenerated.")
        
        initial_branch_id = self.current_branch_id
        message_to_regen_id = self.branches[initial_branch_id].head_message_id
        branch_message_id = self.messages[message_to_regen_id].parent_id
        
        new_branch_id = self.create_branch(branch_message_id)
        self.switch_branch(new_branch_id)
        self.branches[initial_branch_id].status = "inactive"

    def save_to_file(self, filename: str) -> None:
        messages = {}
        branches = {}
        
        for key, value in self.messages.items():
            messages[key] = asdict(value)

        for key, value in self.branches.items():
            branches[key] = asdict(value)

        data = {
            "version" : VERSION,
            "current_branch_id" : self.current_branch_id,
            "messages" : messages,
            "branches" : branches
            }
        
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)

    @classmethod
    def load_from_file(cls, filename: str) -> "Conversation":
        with open(filename, "r", encoding="utf-8") as file:
            data=json.load(file)
        
        conversation=cls.__new__(cls)
        conversation.messages = {}
        conversation.branches = {}
        conversation.current_branch_id = data["current_branch_id"]
            
        for key, value in data["messages"].items():
            conversation.messages[key] = Message.from_dict(value)

        for key, value in data["branches"].items():
            conversation.branches[key] = Branch.from_dict(value)

        return conversation