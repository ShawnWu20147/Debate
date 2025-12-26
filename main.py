from autogen import GroupChat, GroupChatManager, UserProxyAgent
from debate_state import DebateStateMachine
from agents.factory import create_agents
from config import DEBATERS_PER_SIDE, JUDGES_COUNT, base_config, host_model, get_debate_model_assignments

# ============================================================================
# 主程序
# ============================================================================
def main():
    # 显示欢迎信息
    print("\n" + "="*60)
    print("欢迎使用AI辩论系统（独立裁判版）")
    print("="*60)
    
    # 提前生成模型分配
    print("\n正在准备辩论队伍的公司和模型分配...")
    model_assignments = get_debate_model_assignments()
    
    # 显示模型分配结果
    print("\n" + "="*60)
    print("辩论队伍公司和模型分配结果：")
    print("="*60)
    print(f"\n正方队伍：")
    print(f"  公司：{model_assignments['pro']['company']}")
    for i, model in enumerate(model_assignments['pro']['models'], 1):
        print(f"  辩手{i}：{model}")
    
    print(f"\n反方队伍：")
    print(f"  公司：{model_assignments['con']['company']}")
    for i, model in enumerate(model_assignments['con']['models'], 1):
        print(f"  辩手{i}：{model}")
    
    print(f"\n裁判：")
    for i, model in enumerate(model_assignments.get('judges', []), 1):
        print(f"  裁判{i}：{model}")
    
    # 让用户确认是否继续
    print("\n" + "="*60)
    print("是否继续使用以上分配开始辩论？")
    print("="*60)
    user_input = input("输入 'y' 继续，其他任何键退出：").strip().lower()
    
    if user_input != 'y':
        print("\n辩论已取消。")
        return
    
    # 获取辩题
    print("\n请输入辩论辩题：")
    debate_topic = input().strip()
    
    if not debate_topic:
        debate_topic = "人工智能将更多地造福人类而非伤害人类"
        print(f"\n使用默认辩题：{debate_topic}")
    
    print(f"\n辩题确认：{debate_topic}")
    print("\n正在初始化辩论系统...\n")
    
    # 创建状态机
    debate_sm = DebateStateMachine()
    
    # 创建agents（传入状态机引用和预分配的模型）
    moderator, pro_debaters, con_debaters, judges = create_agents(debate_topic, debate_sm, model_assignments)
    
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
    print("="*60)
    print("辩论正式开始")
    print("="*60 + "\n")
    
    try:
        user_proxy.initiate_chat(
            manager,
            message=f"""现在开始关于"{debate_topic}"的辩论。

辩论规则：
1. 开场陈述：正反方各{DEBATERS_PER_SIDE}位辩手依次陈述观点
2. 自由辩论：双方自由交锋
3. 总结陈词：反方和正方的{DEBATERS_PER_SIDE}号辩手总结
4. 独立评分：{JUDGES_COUNT}位裁判各自独立评分（互不干扰）
5. 最终裁决：主持人综合{JUDGES_COUNT}位裁判意见宣布结果

请主持人开始介绍。""",
        )
    except Exception as e:
        print(f"\n辩论过程中出现错误：{e}")
    
    print("\n" + "="*60)
    print("辩论结束")
    print("="*60)

if __name__ == "__main__":
    main()