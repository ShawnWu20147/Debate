from autogen import AssistantAgent

class FinalModeratorAgent(AssistantAgent):
    """最终主持人Agent - 能看到所有裁判评分"""
    
    def __init__(self, name, llm_config, system_message, debate_sm, ui_callback=None):
        super().__init__(name=name, llm_config=llm_config, system_message=system_message)
        self.debate_sm = debate_sm
        self.is_final_announcement = False
        self.ui_callback = ui_callback

    def generate_reply(self, sender=None, **kwargs):
        reply = super().generate_reply(sender=sender, **kwargs)
        if reply and self.ui_callback:
            self.ui_callback(self.name, reply)
        

        return "[主持人]:" + reply

class FilteredAssistantAgent(AssistantAgent):
    """过滤其他裁判消息的助手Agent"""
    
    def __init__(self, name, llm_config, system_message, debate_sm=None, ui_callback=None):
        super().__init__(name=name, llm_config=llm_config, system_message=system_message)
        self.debate_sm = debate_sm
        self.ui_callback = ui_callback
    
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
            reply = super().generate_reply(sender=sender, **kwargs)
            if reply and self.ui_callback:
                self.ui_callback(self.name, reply)
            
            return f"[{self.name}]: {reply}"
        finally:
            # Restore full history to avoid side effects
            self.chat_messages[sender] = original

class DebaterAssistantAgent(AssistantAgent):
    """辩手Agent - 支持界面回调"""
    
    def __init__(self, name, llm_config, system_message, debate_sm=None, ui_callback=None):
        super().__init__(name=name, llm_config=llm_config, system_message=system_message)
        self.debate_sm = debate_sm
        self.ui_callback = ui_callback
    
    def generate_reply(self, sender=None, **kwargs):
        reply = super().generate_reply(sender=sender, **kwargs)
        if reply and self.ui_callback:
            self.ui_callback(self.name, reply)

        stateName = self.debate_sm.get_state_name()
        return f"[{stateName}-{self.name}]: {reply}"