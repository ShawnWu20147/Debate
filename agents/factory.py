from config import base_config, host_model, debaters_per_side, judges_count, max_free_debate_turns
from agents.custom_agents import FinalModeratorAgent, FilteredAssistantAgent, DebaterAssistantAgent
from agents.prompts import get_moderator_message, get_debater_message, get_judge_message
from debater_traits import get_trait_info
from autogen import AssistantAgent

# ============================================================================
# 创建Agents
# ============================================================================
def create_agents(debate_topic, debate_sm, model_assignments=None, trait_assignments=None, ui_callback=None, max_free_debate_turns=None, debaters_per_side=2, judges_count=3):
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
        trait_assignments: 预定义的辩手特质分配，格式为:
            {
                "pro": [特质1, 特质2, ...],
                "con": [特质1, 特质2, ...]
            }
        ui_callback: 界面回调函数，用于通知界面更新
        max_free_debate_turns: 自由辩论最大轮次
        debaters_per_side: 每方辩手人数
        judges_count: 裁判人数
    """
    # 使用传递的参数作为实际的辩手人数和裁判人数
    actual_debaters_per_side = debaters_per_side
    actual_judges_count = judges_count
    
    # 主持人（特殊处理final阶段）
    moderator_model = model_assignments.get('moderator_model', host_model)
    moderator = FinalModeratorAgent(
        name="主持人",
        llm_config={"config_list": [{**base_config, "model": moderator_model}]},
        system_message=get_moderator_message(actual_judges_count, max_free_debate_turns),
        debate_sm=debate_sm,
        ui_callback=ui_callback,
    )
    
    # 正方辩手：使用预定义的公司和模型
    pro_company = model_assignments["pro"]["company"]
    pro_models = model_assignments["pro"]["models"]
    print(f"Debug: 正方队伍选择的公司: {pro_company}")
    pro_debaters = []
    
    # 获取正方特质
    pro_traits = trait_assignments.get("pro", []) if trait_assignments else []
    
    for i in range(1, actual_debaters_per_side + 1):
        # 确保有足够的模型，如果不够则循环使用
        pro_model = pro_models[(i-1) % len(pro_models)]
        print(f"Debug: 正方辩手{i}选择的模型: {pro_model}")
        
        # 获取特质信息（支持新的字典格式和旧的字符串格式）
        trait_data = pro_traits[(i-1) % len(pro_traits)] if pro_traits else None
        if isinstance(trait_data, dict):
            # 新格式：{"name": "...", "description": "..."}
            trait_name = trait_data.get("name", "")
            custom_description = trait_data.get("description")
            if trait_name == "自定义" and custom_description:
                # 自定义特质，直接使用用户输入的描述
                trait_prompt = custom_description
            else:
                # 预定义特质，从配置获取
                trait_info_data = get_trait_info(trait_name) if trait_name else {}
                trait_prompt = trait_info_data.get("prompt_addition", "")
        else:
            # 旧格式：字符串
            trait_name = trait_data if trait_data else ""
            trait_info_data = get_trait_info(trait_name) if trait_name else {}
            trait_prompt = trait_info_data.get("prompt_addition", "")
        
        print(f"Debug: 正方辩手{i}的特质: {trait_name}")
        
        debater = DebaterAssistantAgent(
            name=f"正方辩手{i}",
            llm_config={"config_list": [{**base_config, "model": pro_model}], "temperature": 0.5},
            system_message=get_debater_message("pro", i, debate_topic, trait_name, trait_prompt),
            debate_sm=debate_sm,
            ui_callback=ui_callback,
        )
        pro_debaters.append(debater)
    
    # 反方辩手：使用预定义的公司和模型
    con_company = model_assignments["con"]["company"]
    con_models = model_assignments["con"]["models"]
    print(f"Debug: 反方队伍选择的公司: {con_company}")
    con_debaters = []
    
    # 获取反方特质
    con_traits = trait_assignments.get("con", []) if trait_assignments else []
    
    for i in range(1, actual_debaters_per_side + 1):
        # 确保有足够的模型，如果不够则循环使用
        con_model = con_models[(i-1) % len(con_models)]
        print(f"Debug: 反方辩手{i}选择的模型: {con_model}")
        
        # 获取特质信息（支持新的字典格式和旧的字符串格式）
        trait_data = con_traits[(i-1) % len(con_traits)] if con_traits else None
        if isinstance(trait_data, dict):
            # 新格式：{"name": "...", "description": "..."}
            trait_name = trait_data.get("name", "")
            custom_description = trait_data.get("description")
            if trait_name == "自定义" and custom_description:
                # 自定义特质，直接使用用户输入的描述
                trait_prompt = custom_description
            else:
                # 预定义特质，从配置获取
                trait_info_data = get_trait_info(trait_name) if trait_name else {}
                trait_prompt = trait_info_data.get("prompt_addition", "")
        else:
            # 旧格式：字符串
            trait_name = trait_data if trait_data else ""
            trait_info_data = get_trait_info(trait_name) if trait_name else {}
            trait_prompt = trait_info_data.get("prompt_addition", "")
        
        print(f"Debug: 反方辩手{i}的特质: {trait_name}")
        
        debater = DebaterAssistantAgent(
            name=f"反方辩手{i}",
            llm_config={"config_list": [{**base_config, "model": con_model}], "temperature": 0.5},
            system_message=get_debater_message("con", i, debate_topic, trait_name, trait_prompt),
            debate_sm=debate_sm,
            ui_callback=ui_callback,
        )
        con_debaters.append(debater)
    
    # 裁判（独立评分）
    judges = []
    # 获取预分配的裁判模型
    judge_models = model_assignments.get('judges', [])
    for i in range(1, actual_judges_count + 1):
        # 使用预分配的模型或默认模型
        current_judge_model = judge_models[i-1] if i <= len(judge_models) else "qwen/qwen3-235b-a22b-2507"
        print(f"Debug: 裁判{i}选择的模型: {current_judge_model}")
        judge = FilteredAssistantAgent(
            name=f"裁判{i}",
            llm_config={"config_list": [{**base_config, "model": current_judge_model}]},
            system_message=get_judge_message(),
            debate_sm=debate_sm,
            ui_callback=ui_callback,
        )
        judges.append(judge)
    
    return moderator, pro_debaters, con_debaters, judges