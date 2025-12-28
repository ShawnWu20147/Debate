import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import threading
import queue
from config import get_debate_model_assignments, update_config
import datetime

class DebateUI:
    """辩论界面类"""
    
    def __init__(self, debate_func):
        self.debate_func = debate_func
        self.root = tk.Tk()
        self.root.title("AI辩论系统")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
        # 消息队列，用于在后台线程和UI线程之间传递消息
        self.message_queue = queue.Queue()
        
        # 当前发言者
        self.current_speaker = None
        
        # 辩论历史记录
        self.debate_history = []
        
        # 创建界面布局
        self.create_widgets()
        
        # 启动消息处理线程
        self.root.after(100, self.process_messages)
        
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置行和列的权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=0)
        main_frame.rowconfigure(0, weight=0)
        main_frame.rowconfigure(1, weight=1)
        
        # 顶部框架：辩题输入和控制按钮
        top_frame = ttk.Frame(main_frame, padding="5")
        top_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # 辩题标签和输入框（第一行）
        ttk.Label(top_frame, text="辩论辩题：").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.topic_var = tk.StringVar()
        self.topic_entry = ttk.Entry(top_frame, textvariable=self.topic_var, width=100)
        self.topic_entry.grid(row=0, column=1, columnspan=11, padx=5, pady=5, sticky=(tk.W, tk.E))
        self.topic_entry.insert(0, "人工智能将更多地造福人类而非伤害人类")
        
        # 参数配置区（第二行）
        ttk.Label(top_frame, text="参数配置：").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        
        # 每方辩手人数
        ttk.Label(top_frame, text="每方辩手：").grid(row=1, column=1, padx=2, pady=5, sticky=tk.W)
        self.debaters_per_side_var = tk.StringVar(value="2")
        self.debaters_per_side_entry = ttk.Spinbox(top_frame, from_=1, to=5, textvariable=self.debaters_per_side_var, width=3)
        self.debaters_per_side_entry.grid(row=1, column=2, padx=2, pady=5)
        
        # 自由辩论轮数
        ttk.Label(top_frame, text="自由辩论轮数：").grid(row=1, column=3, padx=2, pady=5, sticky=tk.W)
        self.free_debate_turns_var = tk.StringVar(value="4")
        self.free_debate_turns_entry = ttk.Spinbox(top_frame, from_=1, to=10, textvariable=self.free_debate_turns_var, width=3)
        self.free_debate_turns_entry.grid(row=1, column=4, padx=2, pady=5)
        
        # 裁判人数
        ttk.Label(top_frame, text="裁判人数：").grid(row=1, column=5, padx=2, pady=5, sticky=tk.W)
        self.judges_count_var = tk.StringVar(value="3")
        self.judges_count_entry = ttk.Spinbox(top_frame, from_=1, to=5, textvariable=self.judges_count_var, width=3)
        self.judges_count_entry.grid(row=1, column=6, padx=2, pady=5)
        
        # 初始化配置按钮
        self.init_config_button = ttk.Button(top_frame, text="初始化配置", command=self.init_config)
        self.init_config_button.grid(row=1, column=7, padx=5, pady=5)
        
        # 开始按钮
        self.start_button = ttk.Button(top_frame, text="开始辩论", command=self.start_debate)
        self.start_button.grid(row=1, column=8, padx=5, pady=5)
        
        # 重新开始按钮
        self.restart_button = ttk.Button(top_frame, text="重新开始", command=self.restart_debate)
        self.restart_button.grid(row=1, column=9, padx=5, pady=5)
        
        # 左侧框架：辩论舞台
        left_frame = ttk.Frame(main_frame, padding="5")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        left_frame.columnconfigure(0, weight=1)
        left_frame.columnconfigure(1, weight=1)
        left_frame.rowconfigure(0, weight=1)
        left_frame.rowconfigure(1, weight=1)
        left_frame.rowconfigure(2, weight=1)
        
        # 主持人区域
        self.moderator_frame = ttk.LabelFrame(left_frame, text="主持人", padding="10")
        self.moderator_frame.grid(row=0, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        # 主持人姓名显示框
        self.moderator_name_label = ttk.Label(self.moderator_frame, text="", font=("Arial", 12, "bold"), 
                                             background="#4CAF50", foreground="white", 
                                             relief="ridge", borderwidth=2, padding=5)
        self.moderator_name_label.pack(pady=(0, 5))
        
        self.moderator_text = scrolledtext.ScrolledText(self.moderator_frame, wrap=tk.WORD, height=8, state=tk.DISABLED)
        self.moderator_text.pack(fill=tk.BOTH, expand=True)
        
        # 正方区域
        self.pro_frame = ttk.LabelFrame(left_frame, text="正方", padding="10")
        self.pro_frame.grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 正方当前发言者姓名显示框
        self.pro_name_label = ttk.Label(self.pro_frame, text="", font=("Arial", 12, "bold"), 
                                      background="#2196F3", foreground="white", 
                                      relief="ridge", borderwidth=2, padding=5)
        self.pro_name_label.pack(pady=(0, 5))
        
        self.pro_text = scrolledtext.ScrolledText(self.pro_frame, wrap=tk.WORD, height=20, state=tk.DISABLED)
        self.pro_text.pack(fill=tk.BOTH, expand=True)
        
        # 反方区域
        self.con_frame = ttk.LabelFrame(left_frame, text="反方", padding="10")
        self.con_frame.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 反方当前发言者姓名显示框
        self.con_name_label = ttk.Label(self.con_frame, text="", font=("Arial", 12, "bold"), 
                                      background="#F44336", foreground="white", 
                                      relief="ridge", borderwidth=2, padding=5)
        self.con_name_label.pack(pady=(0, 5))
        
        self.con_text = scrolledtext.ScrolledText(self.con_frame, wrap=tk.WORD, height=20, state=tk.DISABLED)
        self.con_text.pack(fill=tk.BOTH, expand=True)
        
        # 评委区域
        self.judges_frame = ttk.LabelFrame(left_frame, text="评委", padding="10")
        self.judges_frame.grid(row=2, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        # 评委当前发言者姓名显示框
        self.judges_name_label = ttk.Label(self.judges_frame, text="", font=("Arial", 12, "bold"), 
                                          background="#FF9800", foreground="white", 
                                          relief="ridge", borderwidth=2, padding=5)
        self.judges_name_label.pack(pady=(0, 5))
        
        self.judges_text = scrolledtext.ScrolledText(self.judges_frame, wrap=tk.WORD, height=8, state=tk.DISABLED)
        self.judges_text.pack(fill=tk.BOTH, expand=True)
        
        # 右侧框架：辩论历史
        right_frame = ttk.LabelFrame(main_frame, text="辩论历史", padding="10")
        right_frame.grid(row=1, column=1, padx=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)
        
        self.history_text = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, width=40)
        self.history_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 导出按钮（右下角）
        self.export_button = ttk.Button(main_frame, text="导出本场辩论", command=self.export_debate)
        self.export_button.grid(row=2, column=1, padx=5, pady=5, sticky=(tk.E, tk.S))
    
    def init_config(self):
        """初始化配置并显示模型分配信息"""
        # 获取当前配置参数
        debaters_per_side = int(self.debaters_per_side_var.get())
        free_debate_turns = int(self.free_debate_turns_var.get())
        judges_count = int(self.judges_count_var.get())
        
        # 更新配置
        update_config(
            debaters_per_side=debaters_per_side,
            judges_count=judges_count,
            max_free_debate_turns=free_debate_turns
        )
        
        # 生成模型分配
        model_assignments = get_debate_model_assignments()
        
        # 构建配置信息
        config_info = "\n" + "="*50 + "\n"
        config_info += "        辩论系统配置信息        \n"
        config_info += "="*50 + "\n\n"
        
        config_info += "【辩论参数】\n"
        config_info += "-"*20 + "\n"
        config_info += f"每方辩手人数：{debaters_per_side}\n"
        config_info += f"自由辩论轮数：{free_debate_turns}\n"
        config_info += f"裁判人数：{judges_count}\n"
        
        config_info += "\n【正方队伍配置】\n"
        config_info += "-"*20 + "\n"
        config_info += f"所属公司：{model_assignments['pro']['company']}\n"
        config_info += "辩手分配：\n"
        for i, model in enumerate(model_assignments['pro']['models'], 1):
            config_info += f"  • 辩手{i}：{model}\n"
        
        config_info += "\n【反方队伍配置】\n"
        config_info += "-"*20 + "\n"
        config_info += f"所属公司：{model_assignments['con']['company']}\n"
        config_info += "辩手分配：\n"
        for i, model in enumerate(model_assignments['con']['models'], 1):
            config_info += f"  • 辩手{i}：{model}\n"
        
        config_info += "\n【裁判配置】\n"
        config_info += "-"*20 + "\n"
        config_info += "裁判分配：\n"
        for i, model in enumerate(model_assignments.get('judges', []), 1):
            config_info += f"  • 裁判{i}：{model}\n"
        
        config_info += "\n" + "="*50
        
        # 清空历史记录，避免重复
        self.debate_history.clear()
        # 直接添加到历史记录，不通过show_message
        self.debate_history.append(("配置信息", config_info))
        self.update_history_text()
    
    def start_debate(self):
        """开始辩论"""
        topic = self.topic_var.get().strip()
        if not topic:
            self.show_message("主持人", "请输入辩论辩题！")
            return
        
        # 禁用开始按钮
        self.start_button.config(state=tk.DISABLED)
        
        # 清空所有聊天框，但保留辩论历史记录中的配置信息
        self.clear_all_texts()
        
        # 添加辩论开始提示信息
        debate_start_info = f"=== 辩论开始 ===\n\n辩题：{topic}\n\n让我们开始这场精彩的辩论！\n"
        debate_start_info += "="*30
        self.debate_history.append(("系统消息", debate_start_info))
        self.update_history_text()
        
        # 获取配置参数
        debaters_per_side = int(self.debaters_per_side_var.get())
        free_debate_turns = int(self.free_debate_turns_var.get())
        judges_count = int(self.judges_count_var.get())
        
        # 在后台线程中运行辩论，传递配置参数
        threading.Thread(
            target=self.debate_func, 
            args=(topic, self.ui_callback, debaters_per_side, judges_count, free_debate_turns), 
            daemon=True
        ).start()
    
    def restart_debate(self):
        """重新开始辩论"""
        self.start_button.config(state=tk.NORMAL)
        self.clear_all_texts()
        self.debate_history.clear()
        self.current_speaker = None
        
    def clear_all_texts(self):
        """清空所有文本框"""
        self.moderator_text.config(state=tk.NORMAL)
        self.pro_text.config(state=tk.NORMAL)
        self.con_text.config(state=tk.NORMAL)
        self.judges_text.config(state=tk.NORMAL)
        self.history_text.config(state=tk.NORMAL)
        
        self.moderator_text.delete(1.0, tk.END)
        self.pro_text.delete(1.0, tk.END)
        self.con_text.delete(1.0, tk.END)
        self.judges_text.delete(1.0, tk.END)
        self.history_text.delete(1.0, tk.END)
        
        self.moderator_text.config(state=tk.DISABLED)
        self.pro_text.config(state=tk.DISABLED)
        self.con_text.config(state=tk.DISABLED)
        self.judges_text.config(state=tk.DISABLED)
        self.history_text.config(state=tk.DISABLED)
    
    def ui_callback(self, speaker_name, message):
        """UI回调函数，接收来自Agent的消息"""
        self.message_queue.put((speaker_name, message))
    
    def process_messages(self):
        """处理消息队列中的消息"""
        try:
            while True:
                speaker_name, message = self.message_queue.get_nowait()
                self.show_message(speaker_name, message)
        except queue.Empty:
            pass
        
        # 继续监听消息
        self.root.after(100, self.process_messages)
    
    def show_message(self, speaker_name, message):
        """在界面上显示消息"""
        # 更新当前发言者
        if self.current_speaker:
            self.set_speaker_color(self.current_speaker, "normal")
        
        self.current_speaker = speaker_name
        self.set_speaker_color(speaker_name, "speaking")
        
        # 显示消息
        if speaker_name == "主持人":
            self.moderator_name_label.config(text=speaker_name)
            self.update_text_widget(self.moderator_text, message)
        elif speaker_name.startswith("正方辩手"):
            self.pro_name_label.config(text=speaker_name)
            self.update_text_widget(self.pro_text, message)
        elif speaker_name.startswith("反方辩手"):
            self.con_name_label.config(text=speaker_name)
            self.update_text_widget(self.con_text, message)
        elif speaker_name.startswith("裁判"):
            self.judges_name_label.config(text=speaker_name)
            self.update_text_widget(self.judges_text, message)
        
        # 更新历史记录
        self.debate_history.append((speaker_name, message))
        self.update_history_text()
    
    def update_text_widget(self, widget, message):
        """更新文本组件"""
        widget.config(state=tk.NORMAL)
        widget.delete(1.0, tk.END)
        
        # 创建标签样式
        widget.tag_configure("speaker_name", background="#4CAF50", foreground="white", font=("Arial", 10, "bold"))
        
        # 显示消息
        widget.insert(tk.END, message)
        
        # 确保文本可见
        widget.see(tk.END)
        widget.config(state=tk.DISABLED)
    
    def update_history_text(self):
        """更新历史记录文本"""
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete(1.0, tk.END)
        
        # 创建不同角色的标签样式
        self.history_text.tag_configure("moderator", background="#4CAF50", foreground="white", font=('Arial', 10, 'bold'))
        self.history_text.tag_configure("pro", background="#2196F3", foreground="white", font=('Arial', 10, 'bold'))
        self.history_text.tag_configure("con", background="#F44336", foreground="white", font=('Arial', 10, 'bold'))
        self.history_text.tag_configure("judge", background="#FF9800", foreground="white", font=('Arial', 10, 'bold'))
        
        # 显示历史记录，每条记录之间用分隔线分隔
        for i, (speaker, message) in enumerate(self.debate_history):
            if i > 0:
                # 添加明显的分隔线
                self.history_text.insert(tk.END, "\n" + "="*60 + "\n\n")
            
            # 根据发言者类型选择标签
            if speaker == "主持人":
                tag = "moderator"
            elif speaker.startswith("正方辩手"):
                tag = "pro"
            elif speaker.startswith("反方辩手"):
                tag = "con"
            elif speaker.startswith("裁判"):
                tag = "judge"
            else:
                tag = ""
            
            # 插入发言者姓名和消息
            self.history_text.insert(tk.END, f"{speaker}:\n", tag)
            self.history_text.insert(tk.END, f"{message}\n")
        
        self.history_text.see(tk.END)  # 滚动到最后
        self.history_text.config(state=tk.DISABLED)
    
    def set_speaker_color(self, speaker_name, state):
        """设置发言者的颜色状态"""
        # 首先重置所有框架的样式
        self.moderator_frame.config(style="TLabelframe")
        self.pro_frame.config(style="TLabelframe")
        self.con_frame.config(style="TLabelframe")
        self.judges_frame.config(style="TLabelframe")
        
        # 然后为当前发言者所在的框架设置高亮样式
        if state == "speaking":
            if speaker_name == "主持人":
                self.moderator_frame.config(style="Speaking.TLabelframe")
            elif speaker_name.startswith("正方辩手"):
                self.pro_frame.config(style="Speaking.TLabelframe")
            elif speaker_name.startswith("反方辩手"):
                self.con_frame.config(style="Speaking.TLabelframe")
            elif speaker_name.startswith("裁判"):
                self.judges_frame.config(style="Speaking.TLabelframe")
    
    def run(self):
        """运行界面"""
        # 创建样式
        style = ttk.Style()
        style.configure("Speaking.TLabelframe", background="#ffcccc")
        
        self.root.mainloop()
    
    def export_debate(self):
        """导出辩论历史为markdown文件"""
        if not self.debate_history:
            self.show_message("系统消息", "没有辩论历史可导出！")
            return
        
        # 生成默认文件名
        default_filename = f"辩论记录_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        # 打开文件保存对话框
        file_path = filedialog.asksaveasfilename(
            title="导出辩论记录",
            defaultextension=".md",
            filetypes=[("Markdown文件", "*.md"), ("所有文件", "*.*")],
            initialfile=default_filename
        )
        
        if not file_path:
            return  # 用户取消保存
        
        # 构建markdown内容
        markdown_content = "# AI辩论系统 - 辩论记录\n\n"
        
        # 添加辩论元信息
        topic = self.topic_var.get()
        if topic:
            markdown_content += f"## 辩论辩题\n{topic}\n\n"
        
        # 查找配置信息
        has_config = False
        for speaker, message in self.debate_history:
            if speaker == "配置信息":
                markdown_content += f"## 辩论配置\n\n"
                # 将配置信息转换为markdown格式
                for line in message.split('\n'):
                    if line.startswith('【') and line.endswith('】'):
                        markdown_content += f"### {line}\n"
                    elif line.startswith('-'):
                        markdown_content += f"{line}\n"
                    elif line.startswith('  • '):
                        markdown_content += f"{line}\n"
                    elif line.strip():
                        markdown_content += f"{line}\n"
                markdown_content += "\n"
                has_config = True
                break
        
        # 添加辩论历史
        markdown_content += "## 辩论历史\n\n"
        
        for speaker, message in self.debate_history:
            if speaker == "配置信息":
                continue  # 跳过配置信息，已经单独处理
            
            # 添加发言者和内容
            markdown_content += f"### {speaker}\n\n"
            
            # 处理多行消息
            for paragraph in message.split('\n'):
                if paragraph.strip():
                    markdown_content += f"> {paragraph}\n"
            
            markdown_content += "\n---\n\n"
        
        # 保存到文件
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            self.show_message("系统消息", f"辩论记录已成功导出到：{file_path}")
        except Exception as e:
            self.show_message("系统消息", f"导出失败：{str(e)}")