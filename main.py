from autogen import GroupChat, GroupChatManager, UserProxyAgent
from debate_state import DebateStateMachine
from agents.factory import create_agents
from config import debaters_per_side, judges_count, base_config, host_model, get_debate_model_assignments, update_config
from debate_ui import DebateUI

# ============================================================================
# 辩论执行函数
# ============================================================================
def run_debate(debate_topic, ui_callback, debaters_per_side=2, judges_count=3, max_free_debate_turns=4, pro_models=None, con_models=None, judge_models=None, moderator_model=None, pro_traits=None, con_traits=None):
    """执行辩论的函数，用于在UI中调用"""
    # 更新配置参数
    update_config(
        debaters_per_side=debaters_per_side,
        judges_count=judges_count,
        max_free_debate_turns=max_free_debate_turns
    )
    
    # 生成模型分配
    if pro_models and con_models and judge_models:
        # 使用自定义模型分配
        model_assignments = {
            'pro': {'company': '自定义选择', 'models': pro_models},
            'con': {'company': '自定义选择', 'models': con_models},
            'judges': judge_models,
            'moderator_model': moderator_model
        }
    else:
        # 生成默认模型分配
        model_assignments = get_debate_model_assignments(debaters_per_side, judges_count)
    
    # 生成特质分配
    if pro_traits and con_traits:
        trait_assignments = {
            'pro': pro_traits,
            'con': con_traits
        }
    else:
        trait_assignments = None
    
    # 模型配置信息已在UI初始化时显示，此处不再重复输出
    
    # 创建状态机
    print(f"Debug: 创建状态机时的参数 - max_free_debate_turns={max_free_debate_turns}, debaters_per_side={debaters_per_side}, judges_count={judges_count}")
    debate_sm = DebateStateMachine(max_free_debate_turns, debaters_per_side, judges_count)
    
    # 创建agents（传入状态机引用、预分配的模型、UI回调和辩论配置参数）
    moderator, pro_debaters, con_debaters, judges = create_agents(
        debate_topic, debate_sm, model_assignments, trait_assignments, ui_callback, max_free_debate_turns,
        debaters_per_side=debaters_per_side, judges_count=judges_count
    )
    
    # 所有agents列表
    all_agents = [moderator] + pro_debaters + con_debaters + judges
    
    # 创建GroupChat
    groupchat = GroupChat(
        agents=all_agents,
        messages=[],
        max_round=50,
        speaker_selection_method=lambda last_speaker, gc: debate_sm.next_speaker(last_speaker, gc),
        allow_repeat_speaker=False,
    )
    
    # 创建GroupChatManager
    manager = GroupChatManager(
        groupchat=groupchat,
        llm_config={"config_list": [{**base_config, "model": host_model}]},
    )
    
    # 创建用户代理
    user_proxy = UserProxyAgent(
        name="辩论发起人",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=0,
        code_execution_config=False,
    )
    
    # 开始辩论
    try:
        user_proxy.initiate_chat(
            manager,
            message=f"""现在开始关于"{debate_topic}"的辩论。

辩论规则：
1. 开场陈述：正反方各{debaters_per_side}位辩手依次陈述观点
2. 自由辩论：双方自由交锋
3. 总结陈词：反方和正方的{debaters_per_side}号辩手总结
4. 独立评分：{judges_count}位裁判各自独立评分（互不干扰）
5. 最终裁决：主持人综合{judges_count}位裁判意见宣布结果

请主持人开始介绍。""",
        )
    except Exception as e:
        ui_callback("主持人", f"辩论过程中出现错误：{e}")

# ============================================================================
# 主程序
# ============================================================================
def main():
    # 创建辩论界面
    debate_ui = DebateUI(run_debate)
    
    # 运行界面
    debate_ui.run()

if __name__ == "__main__":
    main()