"""
辩手特质配置文件
定义各种辩论风格和对应的行为模式描述
"""

from typing import Dict, List

# 预定义辩手特质类型
DEBATER_TRAITS = {
    "理性数据流": {
        "description": "擅长用数据和事实说话，逻辑严密，论证有据可依",
        "prompt_addition": """
【特质强化：理性数据流】
- 你的辩论风格偏向理性分析，注重数据和事实支撑
- 发言时优先引用权威数据、研究报告、统计数字
- 使用图表、案例分析来支撑论点
- 逻辑链条清晰，论证过程严谨
- 当没有具体数据时，使用合理的逻辑推理
- 避免情绪化表达，保持冷静客观的分析视角
""",
        "characteristics": ["数据驱动", "逻辑严密", "客观理性", "事实支撑"]
    },
    
    "逻辑诡辩流": {
        "description": "擅长发现对方逻辑漏洞，运用反证法和类比推理",
        "prompt_addition": """
【特质强化：逻辑诡辩流】
- 你的辩论风格偏向逻辑分析，擅长发现对方论证的薄弱环节
- 重点关注对方论证的逻辑漏洞、前提假设和推理过程
- 使用反证法、类比推理、归谬法等逻辑技巧
- 善于将复杂问题简化，找出关键矛盾点
- 发言时先破后立，先拆解对方观点再建立自己的论证
- 避免直接正面硬碰，多采用迂回战术
""",
        "characteristics": ["逻辑敏锐", "善于反驳", "类比推理", "反证技巧"]
    },
    
    "心理操控流": {
        "description": "善于洞察人性弱点，通过心理暗示和情感诉求影响判断",
        "prompt_addition": """
【特质强化：心理操控流】
- 你的辩论风格偏向心理分析，善于洞察人的心理弱点
- 善于运用心理学原理，如认知偏差、社会认同等
- 通过情境设定和价值引导影响听众和评委的判断
- 发言时注意语气、节奏和情感渲染
- 善于将抽象问题具体化，让听众产生直观感受
- 避免过度理性，注重情感共鸣和心理暗示
""",
        "characteristics": ["心理洞察", "情感渲染", "情境设定", "价值引导"]
    },
    
    "激情演讲流": {
        "description": "语言富有感染力，善于运用修辞手法和情感表达",
        "prompt_addition": """
【特质强化：激情演讲流】
- 你的辩论风格偏向激情演讲，语言富有感染力
- 善于运用比喻、排比、反问等修辞手法
- 语调起伏变化，节奏感强，具有演讲的韵律美
- 善于煽动情绪，激发听众的共鸣和认同
- 发言时感情饱满，态度坚定，立场鲜明
- 避免平铺直叙，注重语言的感染力和说服力
""",
        "characteristics": ["语言感染力", "修辞技巧", "情感饱满", "演讲韵律"]
    },
    
    "经验实用流": {
        "description": "注重实践经验和现实案例，善于从实际出发论证",
        "prompt_addition": """
【特质强化：经验实用流】
- 你的辩论风格偏向实用主义，注重实践经验和现实案例
- 善于引用工作、生活、社会中的真实案例
- 从可行性、实用性角度论证观点
- 关注政策的实施难度和实际效果
- 发言时以"在我工作经验中"、"从实际情况看"等开头
- 避免空谈理论，多谈实践经验和现实影响
""",
        "characteristics": ["实践经验", "现实案例", "实用主义", "可行性分析"]
    },
    
    "道德评判流": {
        "description": "注重价值判断和道德标准，善于从伦理角度论证",
        "prompt_addition": """
【特质强化：道德评判流】
- 你的辩论风格偏向价值判断，注重道德标准和伦理原则
- 善于从正义、公平、人权等道德维度分析问题
- 引用道德哲学家、伦理学家观点支撑论点
- 关注社会价值观和文化传统的影响
- 发言时体现明确的道德立场和价值追求
- 避免纯粹的功利计算，注重道德正当性
""",
        "characteristics": ["道德标准", "价值判断", "伦理分析", "正义公平"]
    },
    
    "幽默讽刺流": {
        "description": "善于运用幽默和讽刺，让辩论在轻松氛围中展现锋芒",
        "prompt_addition": """
【特质强化：幽默讽刺流】
- 你的辩论风格偏向幽默讽刺，让辩论在轻松氛围中展现锋芒
- 善于运用反讽、双关、调侃等幽默技巧
- 用轻松的方式化解对方的攻击，同时保持攻击力
- 善于用幽默的例子来说明严肃的问题
- 发言时语言风趣，但不失辩论的严谨性
- 避免过度娱乐化，保持幽默的分寸感
""",
        "characteristics": ["幽默技巧", "讽刺艺术", "轻松氛围", "风趣表达"]
    },
    
    "权威引用流": {
        "description": "善于引用权威人物、名言警句和经典理论支撑观点",
        "prompt_addition": """
【特质强化：权威引用流】
- 你的辩论风格偏向权威引用，善于借助名人名言和经典理论
- 引用权威专家、学者、领导人的观点支撑论点
- 运用经典理论、哲学思想、社会科学原理
- 善于将权威观点与当前议题结合
- 发言时体现博学多才，见多识广
- 避免生硬引用，注重权威观点与论证的自然融合
""",
        "characteristics": ["权威引用", "名人名言", "经典理论", "博学多才"]
    }
}

def get_all_trait_names() -> List[str]:
    """获取所有预定义特质的名称列表"""
    return list(DEBATER_TRAITS.keys())

def get_trait_info(trait_name: str) -> Dict:
    """获取指定特质的信息"""
    return DEBATER_TRAITS.get(trait_name, {})

def get_random_trait() -> str:
    """随机获取一个特质名称"""
    import random
    traits = get_all_trait_names()
    return random.choice(traits)

def get_random_traits(count: int) -> List[str]:
    """随机获取指定数量的特质"""
    import random
    traits = get_all_trait_names()
    return random.sample(traits, min(count, len(traits)))

def validate_trait_name(trait_name: str) -> bool:
    """验证特质名称是否有效"""
    return trait_name in DEBATER_TRAITS

def create_custom_trait(description: str) -> Dict:
    """创建自定义特质"""
    return {
        "description": description,
        "prompt_addition": f"""
【特质强化：自定义风格】
- 你的辩论风格特点：{description}
- 请在发言中体现这一特质
- 将这一特点融入你的论证逻辑和表达方式中
""",
        "characteristics": [description]
    }

def add_custom_trait_to_registry(trait_name: str, trait_info: Dict):
    """将自定义特质添加到注册表"""
    global DEBATER_TRAITS
    DEBATER_TRAITS[trait_name] = trait_info

def get_custom_trait_info(trait_name: str) -> Dict:
    """获取自定义特质信息"""
    return DEBATER_TRAITS.get(trait_name, {})

def save_custom_traits_to_file(filepath: str = "custom_traits.json"):
    """保存自定义特质到文件"""
    import json
    import os
    
    # 分离预定义和自定义特质
    predefined_traits = {
        "理性数据流", "逻辑诡辩流", "心理操控流", "激情演讲流", 
        "经验实用流", "道德评判流", "幽默讽刺流", "权威引用流"
    }
    
    custom_traits = {}
    for name, info in DEBATER_TRAITS.items():
        if name not in predefined_traits:
            custom_traits[name] = info
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(custom_traits, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存自定义特质失败: {e}")
        return False

def load_custom_traits_from_file(filepath: str = "custom_traits.json"):
    """从文件加载自定义特质"""
    import json
    import os
    
    if not os.path.exists(filepath):
        return
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            custom_traits = json.load(f)
        
        global DEBATER_TRAITS
        DEBATER_TRAITS.update(custom_traits)
    except Exception as e:
        print(f"加载自定义特质失败: {e}")

def reset_custom_traits():
    """重置所有自定义特质"""
    global DEBATER_TRAITS
    
    # 只保留预定义特质
    predefined_traits = {
        "理性数据流": DEBATER_TRAITS["理性数据流"],
        "逻辑诡辩流": DEBATER_TRAITS["逻辑诡辩流"],
        "心理操控流": DEBATER_TRAITS["心理操控流"],
        "激情演讲流": DEBATER_TRAITS["激情演讲流"],
        "经验实用流": DEBATER_TRAITS["经验实用流"],
        "道德评判流": DEBATER_TRAITS["道德评判流"],
        "幽默讽刺流": DEBATER_TRAITS["幽默讽刺流"],
        "权威引用流": DEBATER_TRAITS["权威引用流"]
    }
    
    DEBATER_TRAITS.clear()
    DEBATER_TRAITS.update(predefined_traits)
    
    # 删除自定义特质文件
    import os
    try:
        os.remove("custom_traits.json")
    except:
        pass