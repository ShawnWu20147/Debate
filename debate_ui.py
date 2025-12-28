import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import threading
import queue
from config import get_debate_model_assignments, update_config, models_by_company, judge_models
import datetime

class DebateConfigWindow:
    """辩论配置窗口类"""
    
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("辩论配置")
        self.window.geometry("1000x700")
        self.window.resizable(True, True)
        self.window.transient(parent)  # 设置为父窗口的子窗口
        self.window.grab_set()  # 模态窗口
        
        # 配置结果
        self.result = None
        
        # 当前配置
        self.debaters_per_side = 2
        self.free_debate_turns = 4
        self.judges_count = 3
        
        # 公司和模型选择
        self.pro_company = ""
        self.con_company = ""
        self.pro_models = []
        self.con_models = []
        self.judge_models = []
        
        # 创建界面
        self.create_widgets()
        
        # 初始化配置
        self.update_company_model_options()
        self.update_debater_model_widgets()
        self.update_judge_model_widgets()
    
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置行和列的权重
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=0)
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        main_frame.rowconfigure(3, weight=0)
        
        # 基本配置区域
        basic_config_frame = ttk.LabelFrame(main_frame, text="基本配置", padding="5")
        basic_config_frame.grid(row=0, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        # 每方辩手人数
        ttk.Label(basic_config_frame, text="每方辩手人数：").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.debaters_per_side_var = tk.IntVar(value=self.debaters_per_side)
        self.debaters_per_side_spinbox = ttk.Spinbox(basic_config_frame, from_=1, to=5, textvariable=self.debaters_per_side_var, width=5,
                                                   command=self.on_debaters_per_side_change)
        self.debaters_per_side_spinbox.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # 自由辩论轮数
        ttk.Label(basic_config_frame, text="自由辩论轮数：").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.free_debate_turns_var = tk.IntVar(value=self.free_debate_turns)
        self.free_debate_turns_spinbox = ttk.Spinbox(basic_config_frame, from_=1, to=10, textvariable=self.free_debate_turns_var, width=5)
        self.free_debate_turns_spinbox.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        
        # 裁判人数
        ttk.Label(basic_config_frame, text="裁判人数：").grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        self.judges_count_var = tk.IntVar(value=self.judges_count)
        self.judges_count_spinbox = ttk.Spinbox(basic_config_frame, from_=1, to=5, textvariable=self.judges_count_var, width=5,
                                              command=self.on_judges_count_change)
        self.judges_count_spinbox.grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)
        
        # 正方配置区域
        pro_frame = ttk.LabelFrame(main_frame, text="正方配置", padding="5")
        pro_frame.grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        pro_frame.columnconfigure(0, weight=1)
        pro_frame.columnconfigure(1, weight=1)
        pro_frame.rowconfigure(0, weight=0)
        pro_frame.rowconfigure(1, weight=1)
        
        # 正方公司选择
        ttk.Label(pro_frame, text="选择公司：").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.pro_company_var = tk.StringVar()
        self.pro_company_combobox = ttk.Combobox(pro_frame, textvariable=self.pro_company_var, width=30)
        self.pro_company_combobox.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        self.pro_company_combobox.bind("<<ComboboxSelected>>", self.on_pro_company_change)
        
        # 正方辩手模型配置
        self.pro_models_frame = ttk.Frame(pro_frame, padding="5")
        self.pro_models_frame.grid(row=1, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.pro_models_frame.columnconfigure(0, weight=1)
        self.pro_models_frame.columnconfigure(1, weight=1)
        
        # 反方配置区域
        con_frame = ttk.LabelFrame(main_frame, text="反方配置", padding="5")
        con_frame.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        con_frame.columnconfigure(0, weight=1)
        con_frame.columnconfigure(1, weight=1)
        con_frame.rowconfigure(0, weight=0)
        con_frame.rowconfigure(1, weight=1)
        
        # 反方公司选择
        ttk.Label(con_frame, text="选择公司：").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.con_company_var = tk.StringVar()
        self.con_company_combobox = ttk.Combobox(con_frame, textvariable=self.con_company_var, width=30)
        self.con_company_combobox.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        self.con_company_combobox.bind("<<ComboboxSelected>>", self.on_con_company_change)
        
        # 反方辩手模型配置
        self.con_models_frame = ttk.Frame(con_frame, padding="5")
        self.con_models_frame.grid(row=1, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.con_models_frame.columnconfigure(0, weight=1)
        self.con_models_frame.columnconfigure(1, weight=1)
        
        # 裁判配置区域
        judges_frame = ttk.LabelFrame(main_frame, text="裁判配置", padding="5")
        judges_frame.grid(row=2, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 裁判模型配置
        self.judges_models_frame = ttk.Frame(judges_frame, padding="5")
        self.judges_models_frame.grid(row=0, column=0, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.judges_models_frame.columnconfigure(0, weight=1)
        self.judges_models_frame.columnconfigure(1, weight=1)
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame, padding="5")
        button_frame.grid(row=3, column=0, columnspan=2, pady=5, sticky=(tk.E))
        
        self.save_button = ttk.Button(button_frame, text="保存配置", command=self.save_config)
        self.save_button.grid(row=0, column=0, padx=5, pady=5)
        
        self.cancel_button = ttk.Button(button_frame, text="取消", command=self.cancel_config)
        self.cancel_button.grid(row=0, column=1, padx=5, pady=5)
    
    def update_company_model_options(self):
        """更新公司和模型选项"""
        # 获取所有公司
        companies = list(models_by_company.keys())
        
        # 设置公司下拉菜单选项
        self.pro_company_combobox['values'] = companies
        self.con_company_combobox['values'] = companies
        
        # 默认选择第一个公司
        if companies:
            self.pro_company_var.set(companies[0])
            self.con_company_var.set(companies[1] if len(companies) > 1 else companies[0])
            self.pro_company = companies[0]
            self.con_company = companies[1] if len(companies) > 1 else companies[0]
    
    def on_debaters_per_side_change(self):
        """每方辩手人数变化时的处理"""
        self.debaters_per_side = self.debaters_per_side_var.get()
        self.update_debater_model_widgets()
    
    def on_judges_count_change(self):
        """裁判人数变化时的处理"""
        self.judges_count = self.judges_count_var.get()
        self.update_judge_model_widgets()
    
    def on_pro_company_change(self, event):
        """正方公司变化时的处理"""
        self.pro_company = self.pro_company_var.get()
        self.update_pro_model_options()
    
    def on_con_company_change(self, event):
        """反方公司变化时的处理"""
        self.con_company = self.con_company_var.get()
        self.update_con_model_options()
    
    def update_pro_model_options(self):
        """更新正方辩手模型选项"""
        # 销毁现有模型选择控件
        for widget in self.pro_models_frame.winfo_children():
            widget.destroy()
        
        # 获取当前公司的模型列表
        models = models_by_company.get(self.pro_company, [])
        
        # 创建新的模型选择控件
        self.pro_models = []
        for i in range(self.debaters_per_side_var.get()):
            ttk.Label(self.pro_models_frame, text=f"辩手{i+1}模型：").grid(row=i, column=0, padx=5, pady=5, sticky=tk.W)
            model_var = tk.StringVar()
            model_combobox = ttk.Combobox(self.pro_models_frame, textvariable=model_var, values=models, width=30)
            model_combobox.grid(row=i, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
            
            # 默认选择第一个模型
            if models:
                model_var.set(models[0])
            
            self.pro_models.append(model_var)
    
    def update_con_model_options(self):
        """更新反方辩手模型选项"""
        # 销毁现有模型选择控件
        for widget in self.con_models_frame.winfo_children():
            widget.destroy()
        
        # 获取当前公司的模型列表
        models = models_by_company.get(self.con_company, [])
        
        # 创建新的模型选择控件
        self.con_models = []
        for i in range(self.debaters_per_side_var.get()):
            ttk.Label(self.con_models_frame, text=f"辩手{i+1}模型：").grid(row=i, column=0, padx=5, pady=5, sticky=tk.W)
            model_var = tk.StringVar()
            model_combobox = ttk.Combobox(self.con_models_frame, textvariable=model_var, values=models, width=30)
            model_combobox.grid(row=i, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
            
            # 默认选择第一个模型
            if models:
                model_var.set(models[0])
            
            self.con_models.append(model_var)
    
    def update_debater_model_widgets(self):
        """更新辩手模型选择控件"""
        self.update_pro_model_options()
        self.update_con_model_options()
    
    def update_judge_model_widgets(self):
        """更新裁判模型选择控件"""
        # 销毁现有模型选择控件
        for widget in self.judges_models_frame.winfo_children():
            widget.destroy()
        
        # 创建新的模型选择控件
        self.judge_models = []
        for i in range(self.judges_count_var.get()):
            ttk.Label(self.judges_models_frame, text=f"裁判{i+1}模型：").grid(row=i, column=0, padx=5, pady=5, sticky=tk.W)
            model_var = tk.StringVar()
            model_combobox = ttk.Combobox(self.judges_models_frame, textvariable=model_var, values=judge_models, width=30)
            model_combobox.grid(row=i, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
            
            # 默认选择第一个模型
            if judge_models:
                model_var.set(judge_models[0])
            
            self.judge_models.append(model_var)
    
    def save_config(self):
        """保存配置"""
        self.result = {
            "debaters_per_side": self.debaters_per_side_var.get(),
            "free_debate_turns": self.free_debate_turns_var.get(),
            "judges_count": self.judges_count_var.get(),
            "pro_company": self.pro_company_var.get(),
            "pro_models": [var.get() for var in self.pro_models],
            "con_company": self.con_company_var.get(),
            "con_models": [var.get() for var in self.con_models],
            "judge_models": [var.get() for var in self.judge_models]
        }
        self.window.destroy()
    
    def cancel_config(self):
        """取消配置"""
        self.result = None
        self.window.destroy()

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
        """显示辩论配置窗口"""
        # 创建配置窗口
        config_window = DebateConfigWindow(self.root)
        
        # 等待配置窗口关闭
        self.root.wait_window(config_window.window)
        
        # 如果用户保存了配置
        if config_window.result:
            # 保存配置结果
            self.config_result = config_window.result
            

            
            # 构建配置信息
            config_info = "\n" + "="*50 + "\n"
            config_info += "        辩论系统配置信息        \n"
            config_info += "="*50 + "\n\n"
            
            config_info += "【辩论参数】\n"
            config_info += "-"*20 + "\n"
            config_info += f"每方辩手人数：{self.config_result['debaters_per_side']}\n"
            config_info += f"自由辩论轮数：{self.config_result['free_debate_turns']}\n"
            config_info += f"裁判人数：{self.config_result['judges_count']}\n"
            
            config_info += "\n【正方队伍配置】\n"
            config_info += "-"*20 + "\n"
            config_info += f"所属公司：{self.config_result['pro_company']}\n"
            config_info += "辩手分配：\n"
            for i, model in enumerate(self.config_result['pro_models'], 1):
                config_info += f"  • 辩手{i}：{model}\n"
            
            config_info += "\n【反方队伍配置】\n"
            config_info += "-"*20 + "\n"
            config_info += f"所属公司：{self.config_result['con_company']}\n"
            config_info += "辩手分配：\n"
            for i, model in enumerate(self.config_result['con_models'], 1):
                config_info += f"  • 辩手{i}：{model}\n"
            
            config_info += "\n【裁判配置】\n"
            config_info += "-"*20 + "\n"
            config_info += "裁判分配：\n"
            for i, model in enumerate(self.config_result['judge_models'], 1):
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
        
        # 检查是否已初始化配置
        if not hasattr(self, 'config_result'):
            self.show_message("主持人", "请先点击'初始化配置'按钮进行配置！")
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
        debaters_per_side = self.config_result["debaters_per_side"]
        free_debate_turns = self.config_result["free_debate_turns"]
        judges_count = self.config_result["judges_count"]
        
        # 获取模型分配
        pro_models = self.config_result["pro_models"]
        con_models = self.config_result["con_models"]
        judge_models = self.config_result["judge_models"]
        
        # 在后台线程中运行辩论，传递配置参数和模型分配
        threading.Thread(
            target=self.debate_func, 
            args=(topic, self.ui_callback, debaters_per_side, judges_count, free_debate_turns, pro_models, con_models, judge_models), 
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