import requests
from config import base_config, host_model

# ============================================================================# 信息提取器# ============================================================================
class InformationExtractor:
    """信息提取器 - 从大模型回复中提取纯文本内容"""
    
    def __init__(self, model=None):
        self.model = model or host_model
        self.base_url = base_config.get("base_url")
        self.api_key = base_config.get("api_key")
    
    def extract(self, text):
        """从文本中提取纯内容"""
        if not text:
            return text
        
        try:
            # 直接调用 openrouter API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://openrouter.ai/",
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的信息提取器。请从给定的文本中提取出人物的真实回答内容，去除所有标记、思考过程和辅助信息。只保留纯文本回答，不要添加任何额外内容。"
                    },
                    {
                        "role": "user",
                        "content": f"请从以下文本中提取出纯回答内容，去除所有标记、思考过程和辅助信息：\n\n{text}"
                    }
                ]
            }
            
            response = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            if result.get("choices"):
                return result["choices"][0]["message"]["content"].strip()
            return text
        except Exception as e:
            print(f"信息提取失败: {e}")
            # 提取失败时返回原始文本
            return text

# 创建全局提取器实例
extractor = InformationExtractor()