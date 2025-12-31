from autogen import AssistantAgent
from agents.extractor import extractor

class FinalModeratorAgent(AssistantAgent):
    """最终主持人Agent - 能看到所有裁判评分"""
    
    def __init__(self, name, llm_config, system_message, debate_sm, ui_callback=None):
        super().__init__(name=name, llm_config=llm_config, system_message=system_message)
        self.debate_sm = debate_sm
        self.is_final_announcement = False
        self.ui_callback = ui_callback

    def generate_reply(self, sender=None, **kwargs):
        max_retries = 3
        for retry in range(max_retries):
            reply = super().generate_reply(sender=sender, **kwargs)
            extracted_reply = extractor.extract(reply)
            
            # 在控制台输出原始回复和提取后的回复
            print(f"原始回复: {reply}")
            print(f"提取回复: {extracted_reply}")
            
            if extracted_reply:
                break
            print(f"回复为空，进行第 {retry + 2} 次重试...")
        
        if extracted_reply and self.ui_callback:
            self.ui_callback(self.name, extracted_reply)
        
        return "[主持人]:" + extracted_reply

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
            max_retries = 3
            for retry in range(max_retries):
                reply = super().generate_reply(sender=sender, **kwargs)
                extracted_reply = extractor.extract(reply)
                
                # 在控制台输出原始回复和提取后的回复
                print(f"原始回复: {reply}")
                print(f"提取回复: {extracted_reply}")
                
                if extracted_reply:
                    break
                print(f"回复为空，进行第 {retry + 2} 次重试...")
            
            if extracted_reply and self.ui_callback:
                self.ui_callback(self.name, extracted_reply)
            
            return f"[{self.name}]: {extracted_reply}"
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
        max_retries = 3
        for retry in range(max_retries):
            reply = super().generate_reply(sender=sender, **kwargs)
            extracted_reply = extractor.extract(reply)
            
            # 在控制台输出原始回复和提取后的回复
            print(f"原始回复: {reply}")
            print(f"提取回复: {extracted_reply}")
            
            if extracted_reply:
                break
            print(f"回复为空，进行第 {retry + 2} 次重试...")
        
        if extracted_reply and self.ui_callback:
            self.ui_callback(self.name, extracted_reply)

        stateName = self.debate_sm.get_state_name()
        return f"[{stateName}-{self.name}]: {extracted_reply}"