import random
from config import max_free_debate_turns

# ============================================================================
# 辩论状态机（带独立裁判评分）
# ============================================================================
class DebateStateMachine:
    """管理辩论流程的状态机，支持裁判独立评分"""
    
    def __init__(self, max_free_debate_turns=None, debaters_per_side=None, judges_count=None):
        self.state = "intro"  # 状态：intro -> opening -> free_debate -> closing -> judging -> final -> end
        self.round_count = 0
        self.free_debate_turns = 0
        self.max_free_debate_turns = max_free_debate_turns  # 允许多次自由辩论（可配置）
        self.debaters_per_side = debaters_per_side  # 每方辩手人数
        self.judges_count = judges_count  # 裁判人数
        
        # 存储辩论内容（不包含裁判评分）
        self.debate_messages = []
        
        # 存储裁判评分（独立保存）
        self.judge_scores = {}
        
        # 当前正在评分的裁判
        self.current_judge_index = 0

    def next_speaker(self, last_speaker, groupchat):
        """根据当前状态决定下一个发言者"""
        
        if self.state == "intro":
            # 主持人介绍
            self.state = "opening"
            self.round_count = 0
            return self._get_agent("主持人", groupchat)
        
        elif self.state == "opening":
            # 开场陈述：正1 反1 正2 反2 正3 反3
            opening_order = []
            for i in range(1, self.debaters_per_side + 1):
                opening_order.extend([f"正方辩手{i}", f"反方辩手{i}"])
            
            if self.round_count < len(opening_order):
                speaker_name = opening_order[self.round_count]
                self.round_count += 1
                return self._get_agent(speaker_name, groupchat)
            else:
                # 开场结束，进入自由辩论
                self.state = "free_debate"
                self.round_count = 0
                self.free_debate_turns = 0
                return self._get_agent("主持人", groupchat)
        
        elif self.state == "free_debate":
            # 主持人宣布后，开始自由辩论
            if last_speaker.name == "主持人":
                self.free_debate_turns = 1
                return self._get_agent("正方辩手1", groupchat)
            
            # 自由辩论：正反方交替，随机选择队内成员
            if self.free_debate_turns >= self.max_free_debate_turns:
                self.state = "closing"
                self.round_count = 1
                return self._get_agent("主持人", groupchat)
            
            # 正反方交替
            if self.free_debate_turns % 2 == 0:
                # 正方回合
                debater_num = random.randint(1, self.debaters_per_side)
                speaker_name = f"正方辩手{debater_num}"
            else:
                # 反方回合
                debater_num = random.randint(1, self.debaters_per_side)
                speaker_name = f"反方辩手{debater_num}"
            
            self.free_debate_turns += 1
            return self._get_agent(speaker_name, groupchat)
        
        elif self.state == "closing":
            # 主持人宣布后，开始总结
            if last_speaker.name == "主持人":
                self.round_count = 0
                return self._get_agent(f"反方辩手{self.debaters_per_side}", groupchat)

            closing_order = [f"正方辩手{self.debaters_per_side}"]
            
            if self.round_count < len(closing_order):
                speaker_name = closing_order[self.round_count]
                self.round_count += 1
                return self._get_agent(speaker_name, groupchat)
            else:
                # 总结结束，进入评判（主持人宣布）
                self.state = "judging"
                self.round_count = 0
                self.current_judge_index = 0
                return self._get_agent("主持人", groupchat)
        
        elif self.state == "judging":
            # 主持人宣布后，裁判依次评分（但彼此看不到对方评分）
            # 裁判评分：裁判1 裁判2 裁判3
            # 关键：每个裁判只看辩论内容，看不到其他裁判的评分
            judge_order = [f"裁判{i}" for i in range(1, self.judges_count + 1)]
            
            if last_speaker.name == "主持人":
                self.current_judge_index = 1  # 下一个裁判是裁判2
                return self._get_agent(judge_order[0], groupchat)
            
            if self.current_judge_index < len(judge_order):
                judge_name = judge_order[self.current_judge_index]
                self.current_judge_index += 1
                return self._get_agent(judge_name, groupchat)
            else:
                # 所有裁判评分完毕，主持人综合宣布结果
                self.state = "final"
                return self._get_agent("主持人", groupchat)
        
        elif self.state == "final":
            # 主持人宣布最终结果后结束
            self.state = "end"
            return None
        
        elif self.state == "end":
            # 辩论结束
            return None
        
        return None
    
    def _get_agent(self, name, groupchat):
        """根据名称获取agent"""
        for agent in groupchat.agents:
            if agent.name == name:
                return agent
        return None
    
    def get_state_description(self):
        """获取当前状态描述（用于调试）"""
        state_desc = {
            "intro": "介绍阶段",
            "opening": f"开场陈述 (第{self.round_count}位)",
            "free_debate": f"自由辩论 (第{self.free_debate_turns}轮)",
            "closing": f"总结陈词 (第{self.round_count}位)",
            "judging": f"裁判评分 (第{self.current_judge_index}位)",
            "final": "主持人宣布结果",
            "end": "辩论结束"
        }
        return state_desc.get(self.state, "未知状态")