from autogen import AssistantAgent

class FinalModeratorAgent(AssistantAgent):
    """最终主持人Agent - 能看到所有裁判评分"""
    
    def __init__(self, name, llm_config, system_message, debate_sm):
        super().__init__(name=name, llm_config=llm_config, system_message=system_message)
        self.debate_sm = debate_sm
        self.is_final_announcement = False

class FilteredAssistantAgent(AssistantAgent):
    """过滤其他裁判消息的助手Agent"""
    
    def generate_reply(self, sender=None, **kwargs):
        # Pull full message history
        messages = self.chat_messages[sender]

        # Filter visibility: exclude messages from other judges
        filtered_messages = []
        for m in messages:
            name = m.get("name", "")
            # Keep all messages except those from other judges
            # A judge message starts with "裁判" (Judge)
            if not (name.startswith("裁判") and name != self.name):
                filtered_messages.append(m)

        # IMPORTANT: temporarily replace messages
        original = self.chat_messages[sender]
        self.chat_messages[sender] = filtered_messages

        try:
            return super().generate_reply(sender=sender, **kwargs)
        finally:
            # Restore full history to avoid side effects
            self.chat_messages[sender] = original