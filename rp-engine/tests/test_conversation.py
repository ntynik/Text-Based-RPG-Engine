from conversation import Conversation

def test_new_conversation():
    conversation = Conversation("Test system prompt")

    assert len(conversation.messages) == 1
    assert len(conversation.branches) == 1

    branch = conversation.branches[conversation.current_branch_id]
    message = conversation.messages[branch.head_message_id]

    assert message.role == "system"
    assert message.content == "Test system prompt"
    assert message.parent_id is None
    assert branch.head_message_id == message.id
    assert branch.status == "active"

def test_parent_chain():
    conversation = Conversation("Test parent chain")

    branch = conversation.branches[conversation.current_branch_id]
    previous_message_id = branch.head_message_id
    conversation.add_user_message("Message 1")
    assert previous_message_id == conversation.messages[branch.head_message_id].parent_id

    previous_message_id = branch.head_message_id
    conversation.add_assistant_message("Message 2")
    assert previous_message_id == conversation.messages[branch.head_message_id].parent_id

    previous_message_id = branch.head_message_id
    conversation.add_user_message("Message 3")
    assert previous_message_id == conversation.messages[branch.head_message_id].parent_id

    previous_message_id = branch.head_message_id
    conversation.add_assistant_message("Message 4")
    assert previous_message_id == conversation.messages[branch.head_message_id].parent_id

def test_message_lineage():
    conversation = Conversation("Test message lineage")

    conversation.add_user_message("Message 1")
    conversation.add_assistant_message("Message 2")
    conversation.add_user_message("Message 3")

    branch_a_id = conversation.current_branch_id
    branch_msg_id = conversation.branches[branch_a_id].head_message_id
    conversation.add_assistant_message("Message 4A")
    branch_a_path = conversation.get_active_path()
    
    branch_b_id = conversation.create_branch(branch_msg_id)
    conversation.switch_branch(branch_b_id)
    conversation.add_assistant_message("Message 4B")
    branch_b_path = conversation.get_active_path()

    root = conversation.messages[branch_a_path[0]]

    assert branch_a_path[:-1] == branch_b_path[:-1]
    assert branch_a_path[-1] != branch_b_path[-1]

    assert root.id == branch_b_path[0]
    assert root.parent_id is None

    assert len(branch_a_path) == len(branch_b_path)

    assert conversation.branches[branch_a_id].head_message_id == branch_a_path[-1]
    assert conversation.branches[branch_b_id].head_message_id == branch_b_path[-1]

    assert conversation.branches[branch_b_id].status == "active"

def test_switch_branch():
    conversation = Conversation("Test switching branches")

    conversation.add_user_message("Message 1")
    branch_a_id = conversation.current_branch_id
    branch_message_id = conversation.branches[branch_a_id].head_message_id
    
    conversation.add_assistant_message("Message 2A")
    branch_a_path = conversation.get_active_path()

    branch_b_id = conversation.create_branch(branch_message_id)
    conversation.switch_branch(branch_b_id)
    branch_b_path = conversation.get_active_path()

    conversation.switch_branch(branch_a_id)
    assert conversation.get_active_path() == branch_a_path
    assert conversation.current_branch_id == branch_a_id
    
    conversation.switch_branch(branch_b_id)
    assert conversation.get_active_path() == branch_b_path
    assert conversation.current_branch_id == branch_b_id
    
    assert branch_a_path != branch_b_path

def test_save_load_persistence():
    conversation = Conversation("Test message lineage")

    conversation.add_user_message("Message 1")
    conversation.add_assistant_message("Message 2")
    conversation.add_user_message("Message 3")

    branch_a_id = conversation.current_branch_id
    branch_msg_id = conversation.branches[branch_a_id].head_message_id

    conversation.add_assistant_message("Message 4A")
    branch_a_path = conversation.get_active_path()
    
    branch_b_id = conversation.create_branch(branch_msg_id)
    conversation.switch_branch(branch_b_id)

    conversation.add_assistant_message("Message 4B")
    branch_b_path = conversation.get_active_path()

    conversation.save_to_file("test.json")
    loaded_conversation = Conversation.load_from_file("test.json")

    assert conversation.messages == loaded_conversation.messages
    assert conversation.branches == loaded_conversation.branches
    assert conversation.current_branch_id == loaded_conversation.current_branch_id

    loaded_conversation.current_branch_id = branch_a_id
    assert loaded_conversation.get_active_path() == branch_a_path

    loaded_conversation.current_branch_id = branch_b_id
    assert loaded_conversation.get_active_path() == branch_b_path