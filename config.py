import os
import random
from dotenv import load_dotenv

# ============================================================================
# 配置加载
# ============================================================================
load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
base_url = os.getenv("OPENROUTER_BASE_URL")

print(f"Debug: Base URL={base_url}")
print(f"Debug: API Key Set={api_key is not None}")

# 模型配置
base_config = {
    "base_url": base_url,
    "api_key": api_key,
}

# 辩论配置
# 默认值，可通过动态参数覆盖
_DEFAULT_DEBATERS_PER_SIDE = 2  # 每方辩手人数
_DEFAULT_JUDGES_COUNT = 3  # 裁判人数
_DEFAULT_MAX_FREE_DEBATE_TURNS = 4  # 自由辩论最大轮次

# 当前使用的配置值
debaters_per_side = _DEFAULT_DEBATERS_PER_SIDE
judges_count = _DEFAULT_JUDGES_COUNT
max_free_debate_turns = _DEFAULT_MAX_FREE_DEBATE_TURNS

def update_config(**kwargs):
    """更新辩论配置参数"""
    global debaters_per_side, judges_count, max_free_debate_turns
    
    if 'debaters_per_side' in kwargs:
        debaters_per_side = kwargs['debaters_per_side']
    if 'judges_count' in kwargs:
        judges_count = kwargs['judges_count']
    if 'max_free_debate_turns' in kwargs:
        max_free_debate_turns = kwargs['max_free_debate_turns']

def get_current_config():
    """获取当前配置"""
    return {
        'debaters_per_side': debaters_per_side,
        'judges_count': judges_count,
        'max_free_debate_turns': max_free_debate_turns
    }

# 为不同角色配置不同模型
host_model = "x-ai/grok-4-fast"

# 裁判模型数组，用于随机分配
judge_models = [
    "qwen/qwen3-235b-a22b-2507",
    "deepseek/deepseek-r1-0528",
    "openai/gpt-4o",
    "anthropic/claude-opus-4.5",
    "qwen/qwen3-vl-235b-a22b-thinking",
    "moonshotai/kimi-k2-thinking"
    ]

models_by_company = {
    "Anthropic": [
        "anthropic/claude-opus-4.1",
        "anthropic/claude-opus-4.5",
        "anthropic/claude-haiku-4.5",
        "anthropic/claude-sonnet-4",
        "anthropic/claude-sonnet-4.5"
    ],

    "OpenAI": [
        "openai/gpt-4o",
        "openai/gpt-4o-2024-08-06",
    ],

    "Alibaba_Qwen": [
        "qwen/qwen3-235b-a22b-2507",
        "qwen/qwen3-32b",
        "qwen/qwen3-235b-a22b",
    ],

    "DeepSeek": [
        "deepseek/deepseek-v3.2",
        "deepseek/deepseek-chat-v3.1"
    ],

    "Moonshot": [
        "moonshotai/kimi-k2",
        "moonshotai/kimi-k2-0905"
    ],

    "xAI": [
        "x-ai/grok-3",
        "x-ai/grok-4",
        "x-ai/grok-4-fast",
        "x-ai/grok-4.1-fast",
    ],
}


def get_random_company():
    """随机选择一个公司"""
    companies = list(models_by_company.keys())
    return random.choice(companies)


def get_random_model_from_company(company):
    """从指定公司中随机选择一个模型"""
    if company in models_by_company:
        return random.choice(models_by_company[company])
    raise ValueError(f"Company {company} not found in models_by_company")


def get_random_judge_model():
    """从裁判模型数组中随机选择一个模型"""
    return random.choice(judge_models)


def get_debate_model_assignments():
    """获取所有辩手的公司和模型分配"""
    # 正方队伍：选择一个公司，然后为每个辩手分配模型
    pro_company = get_random_company()
    pro_models = [get_random_model_from_company(pro_company) for _ in range(debaters_per_side)]
    
    # 反方队伍：选择一个公司，然后为每个辩手分配模型
    con_company = get_random_company()
    con_models = [get_random_model_from_company(con_company) for _ in range(debaters_per_side)]
    
    # 裁判模型分配
    judge_models_assigned = [get_random_judge_model() for _ in range(judges_count)]
    
    return {
        "pro": {
            "company": pro_company,
            "models": pro_models
        },
        "con": {
            "company": con_company,
            "models": con_models
        },
        "judges": judge_models_assigned
    }
