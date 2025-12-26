from config import base_config, host_model, debaters_per_side, judges_count, max_free_debate_turns
from agents.custom_agents import FinalModeratorAgent, FilteredAssistantAgent, DebaterAssistantAgent
from agents.prompts import get_moderator_message, get_debater_message, get_judge_message
from autogen import AssistantAgent

# ============================================================================
# 创建Agents
# ============================================================================
def create_agents(debate_topic, debate_sm, model_assignments=None, ui_callback=None, max_free_debate_turns=None):
    """创建所有辩论agents
    
    Args:
        debate_topic: 辩论辩题
        debate_sm: 辩论状态机实例
        model_assignments: 预定义的公司和模型分配，格式为:
            {
                "pro": {
                    "company": "公司名称",
                    "models": [模型1, 模型2, ...]
                },
                "con": {
                    "company": "公司名称",
                    "models": [模型1, 模型2, ...]
                }
            }
        ui_callback: 界面回调函数，用于通知界面更新
    """
    
    # 主持人（特殊处理final阶段）
    moderator = FinalModeratorAgent(
        name="主持人",
        llm_config={"config_list": [{**base_config, "model": host_model}]},
        system_message=get_moderator_message(judges_count, max_free_debate_turns),
        debate_sm=debate_sm,
        ui_callback=ui_callback,
    )
    
    # 正方辩手：使用预定义的公司和模型
    pro_company = model_assignments["pro"]["company"]
    pro_models = model_assignments["pro"]["models"]
    print(f"Debug: 正方队伍选择的公司: {pro_company}")
    pro_debaters = []
    for i in range(1, debaters_per_side + 1):
        pro_model = pro_models[i-1]
        print(f"Debug: 正方辩手{i}选择的模型: {pro_model}")
        debater = DebaterAssistantAgent(
            name=f"正方辩手{i}",
            llm_config={"config_list": [{**base_config, "model": pro_model}], "temperature": 0.5},
            system_message=get_debater_message("pro", i, debate_topic),
            ui_callback=ui_callback,
        )
        pro_debaters.append(debater)
    
    # 反方辩手：使用预定义的公司和模型
    con_company = model_assignments["con"]["company"]
    con_models = model_assignments["con"]["models"]
    print(f"Debug: 反方队伍选择的公司: {con_company}")
    con_debaters = []
    for i in range(1, debaters_per_side + 1):
        con_model = con_models[i-1]
        print(f"Debug: 反方辩手{i}选择的模型: {con_model}")
        debater = DebaterAssistantAgent(
            name=f"反方辩手{i}",
            llm_config={"config_list": [{**base_config, "model": con_model}], "temperature": 0.5},
            system_message=get_debater_message("con", i, debate_topic),
            ui_callback=ui_callback,
        )
        con_debaters.append(debater)
    
    # 裁判（独立评分）
    judges = []
    # 获取预分配的裁判模型
    judge_models = model_assignments.get('judges', [])
    for i in range(1, judges_count + 1):
        # 使用预分配的模型或默认模型
        current_judge_model = judge_models[i-1] if i <= len(judge_models) else "qwen/qwen3-235b-a22b-2507"
        print(f"Debug: 裁判{i}选择的模型: {current_judge_model}")
        judge = FilteredAssistantAgent(
            name=f"裁判{i}",
            llm_config={"config_list": [{**base_config, "model": current_judge_model}]},
            system_message=get_judge_message(),
            ui_callback=ui_callback,
        )
        judges.append(judge)
    
    return moderator, pro_debaters, con_debaters, judges