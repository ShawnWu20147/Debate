import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import threading
import queue
from config import get_debate_model_assignments, update_config, models_by_company, judge_models
from debater_traits import get_all_trait_names, get_trait_info, get_random_trait, create_custom_trait
import datetime

class DebateConfigWindow:
    """辩论配置窗口类"""
    
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("辩论配置")
        self.window.resizable(True, True)
        self.window.transient(parent)  # 设置为父窗口的子窗口
        self.window.grab_set()  # 模态窗口
        
        # 设置窗口大小和位置（居中于父窗口）
        window_width = 1000
        window_height = 800
        
        # 获取父窗口的位置和大小
        parent.update_idletasks()  # 确保获取到正确的尺寸
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        # 计算居中位置
        x = parent_x + (parent_width - window_width) // 2
        y = parent_y + (parent_height - window_height) // 2
        
        # 确保窗口不会超出屏幕
        x = max(0, x)
        y = max(0, y)
        
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.window.minsize(900, 600)  # 设置最小窗口大小
        
        # 绑定窗口关闭事件
        self.window.protocol("WM_DELETE_WINDOW", self.on_window_close)
        
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
        
        # 辩手特质选择
        self.pro_traits = []
        self.con_traits = []
        
        # 创建界面
        self.create_widgets()
        
        # 初始化配置
        self.update_company_model_options()
        self.update_debater_model_widgets()
        self.update_debater_traits_widgets()
        self.update_judge_model_widgets()
    
    def create_widgets(self):
        """创建界面组件"""
        # 主框架 - 使用Canvas实现滚动
        self.main_canvas = tk.Canvas(self.window)
        self.main_scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=self.main_canvas.yview)
        self.main_canvas.configure(yscrollcommand=self.main_scrollbar.set)
        
        self.main_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 创建内部框架
        main_frame = ttk.Frame(self.main_canvas, padding="10")
        self.main_canvas_window = self.main_canvas.create_window((0, 0), window=main_frame, anchor="nw")
        
        # 配置行和列的权重
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=0)
        main_frame.rowconfigure(1, weight=0)
        main_frame.rowconfigure(2, weight=1)
        main_frame.rowconfigure(3, weight=0)
        main_frame.rowconfigure(4, weight=0)
        
        # 绑定滚动区域更新事件
        def on_frame_configure(event):
            self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        
        def on_canvas_configure(event):
            # 使内部框架宽度跟随canvas宽度
            self.main_canvas.itemconfig(self.main_canvas_window, width=event.width)
        
        main_frame.bind("<Configure>", on_frame_configure)
        self.main_canvas.bind("<Configure>", on_canvas_configure)
        
        # 绑定鼠标滚轮事件
        def on_mousewheel(event):
            self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.main_canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # 基本配置区域
        basic_config_frame = ttk.LabelFrame(main_frame, text="基本配置", padding="5")
        basic_config_frame.grid(row=0, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        # 每方辩手人数
        ttk.Label(basic_config_frame, text="每方辩手人数：").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.debaters_per_side_var = tk.IntVar(value=self.debaters_per_side)
        self.debaters_per_side_spinbox = ttk.Spinbox(basic_config_frame, from_=1, to=5, textvariable=self.debaters_per_side_var, width=5,
                                                   command=self.on_debaters_per_side_change)
        self.debaters_per_side_spinbox.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        # 绑定键盘事件，支持手动输入
        self.debaters_per_side_spinbox.bind("<Return>", lambda e: self.on_debaters_per_side_change())
        self.debaters_per_side_spinbox.bind("<FocusOut>", lambda e: self.on_debaters_per_side_change())
        
        # 自由辩论轮数
        ttk.Label(basic_config_frame, text="自由辩论轮数：").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.free_debate_turns_var = tk.IntVar(value=self.free_debate_turns)
        self.free_debate_turns_spinbox = ttk.Spinbox(basic_config_frame, from_=1, to=100, textvariable=self.free_debate_turns_var, width=5)
        self.free_debate_turns_spinbox.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        # 绑定键盘事件，支持手动输入
        self.free_debate_turns_spinbox.bind("<Return>", lambda e: self.on_free_debate_turns_change())
        self.free_debate_turns_spinbox.bind("<FocusOut>", lambda e: self.on_free_debate_turns_change())
        
        # 裁判人数
        ttk.Label(basic_config_frame, text="裁判人数：").grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        self.judges_count_var = tk.IntVar(value=self.judges_count)
        self.judges_count_spinbox = ttk.Spinbox(basic_config_frame, from_=1, to=5, textvariable=self.judges_count_var, width=5,
                                              command=self.on_judges_count_change)
        self.judges_count_spinbox.grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)
        # 绑定键盘事件，支持手动输入
        self.judges_count_spinbox.bind("<Return>", lambda e: self.on_judges_count_change())
        self.judges_count_spinbox.bind("<FocusOut>", lambda e: self.on_judges_count_change())
        
        # 主持人配置区域
        moderator_frame = ttk.LabelFrame(main_frame, text="主持人配置", padding="5")
        moderator_frame.grid(row=1, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        # 主持人公司选择
        ttk.Label(moderator_frame, text="主持人公司：").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.moderator_company_var = tk.StringVar()
        self.moderator_company_combobox = ttk.Combobox(moderator_frame, textvariable=self.moderator_company_var, width=30, state="readonly")
        self.moderator_company_combobox.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        self.moderator_company_combobox.bind("<<ComboboxSelected>>", self.on_moderator_company_change)
        
        # 主持人模型选择
        ttk.Label(moderator_frame, text="主持人模型：").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.moderator_model_var = tk.StringVar()
        self.moderator_model_combobox = ttk.Combobox(moderator_frame, textvariable=self.moderator_model_var, width=30, state="readonly")
        self.moderator_model_combobox.grid(row=0, column=3, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # 正方配置区域
        pro_frame = ttk.LabelFrame(main_frame, text="正方配置", padding="5")
        pro_frame.grid(row=2, column=0, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        pro_frame.columnconfigure(0, weight=1)
        pro_frame.columnconfigure(1, weight=1)
        pro_frame.rowconfigure(0, weight=0)
        pro_frame.rowconfigure(1, weight=1)
        
        # 正方公司选择
        ttk.Label(pro_frame, text="选择公司：").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.pro_company_var = tk.StringVar()
        self.pro_company_combobox = ttk.Combobox(pro_frame, textvariable=self.pro_company_var, width=30, state="readonly")
        self.pro_company_combobox.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        self.pro_company_combobox.bind("<<ComboboxSelected>>", self.on_pro_company_change)
        
        # 正方辩手特质配置
        self.pro_traits_frame = ttk.Frame(pro_frame, padding="5")
        self.pro_traits_frame.grid(row=1, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        self.pro_traits_frame.columnconfigure(0, weight=1)
        self.pro_traits_frame.columnconfigure(1, weight=1)
        
        # 正方辩手模型配置
        self.pro_models_frame = ttk.Frame(pro_frame, padding="5")
        self.pro_models_frame.grid(row=2, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.pro_models_frame.columnconfigure(0, weight=1)
        self.pro_models_frame.columnconfigure(1, weight=1)
        
        # 反方配置区域
        con_frame = ttk.LabelFrame(main_frame, text="反方配置", padding="5")
        con_frame.grid(row=2, column=1, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        con_frame.columnconfigure(0, weight=1)
        con_frame.columnconfigure(1, weight=1)
        con_frame.rowconfigure(0, weight=0)
        con_frame.rowconfigure(1, weight=1)
        
        # 反方公司选择
        ttk.Label(con_frame, text="选择公司：").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.con_company_var = tk.StringVar()
        self.con_company_combobox = ttk.Combobox(con_frame, textvariable=self.con_company_var, width=30, state="readonly")
        self.con_company_combobox.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        self.con_company_combobox.bind("<<ComboboxSelected>>", self.on_con_company_change)
        
        # 反方辩手特质配置
        self.con_traits_frame = ttk.Frame(con_frame, padding="5")
        self.con_traits_frame.grid(row=1, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        self.con_traits_frame.columnconfigure(0, weight=1)
        self.con_traits_frame.columnconfigure(1, weight=1)
        
        # 反方辩手模型配置
        self.con_models_frame = ttk.Frame(con_frame, padding="5")
        self.con_models_frame.grid(row=2, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.con_models_frame.columnconfigure(0, weight=1)
        self.con_models_frame.columnconfigure(1, weight=1)
        
        # 裁判配置区域
        judges_frame = ttk.LabelFrame(main_frame, text="裁判配置", padding="5")
        judges_frame.grid(row=3, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 裁判模型配置
        self.judges_models_frame = ttk.Frame(judges_frame, padding="5")
        self.judges_models_frame.grid(row=0, column=0, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.judges_models_frame.columnconfigure(0, weight=1)
        self.judges_models_frame.columnconfigure(1, weight=1)
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame, padding="5")
        button_frame.grid(row=4, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        # 左侧：功能按钮
        left_button_frame = ttk.Frame(button_frame)
        left_button_frame.grid(row=0, column=0, sticky=tk.W)
        
        # 特质随机化按钮
        self.randomize_traits_button = ttk.Button(left_button_frame, text="一键随机化特质", command=self.randomize_all_traits)
        self.randomize_traits_button.grid(row=0, column=0, padx=5, pady=5)
        
        # 右侧：保存取消按钮
        right_button_frame = ttk.Frame(button_frame)
        right_button_frame.grid(row=0, column=1, sticky=tk.E)
        
        self.save_button = ttk.Button(right_button_frame, text="保存配置", command=self.save_config)
        self.save_button.grid(row=0, column=0, padx=5, pady=5)
        
        self.cancel_button = ttk.Button(right_button_frame, text="取消", command=self.cancel_config)
        self.cancel_button.grid(row=0, column=1, padx=5, pady=5)
        
        # 配置按钮框架的列权重
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
    
    def update_company_model_options(self):
        """更新公司和模型选项"""
        # 获取所有公司
        companies = list(models_by_company.keys())
        
        # 设置公司下拉菜单选项
        self.pro_company_combobox['values'] = companies
        self.con_company_combobox['values'] = companies
        self.moderator_company_combobox['values'] = companies
        
        # 默认选择第一个公司
        if companies:
            self.pro_company_var.set(companies[0])
            self.con_company_var.set(companies[1] if len(companies) > 1 else companies[0])
            self.moderator_company_var.set(companies[0] if len(companies) > 0 else "")
            self.pro_company = companies[0]
            self.con_company = companies[1] if len(companies) > 1 else companies[0]
            self.moderator_company = companies[0] if len(companies) > 0 else ""
            
            # 更新主持人模型选项
            self.update_moderator_model_options()
    
    def on_debaters_per_side_change(self):
        """每方辩手人数变化时的处理"""
        try:
            value = self.debaters_per_side_var.get()
            # 验证范围
            if value < 1:
                value = 1
                self.debaters_per_side_var.set(value)
            elif value > 5:
                value = 5
                self.debaters_per_side_var.set(value)
            self.debaters_per_side = value
            self.update_debater_model_widgets()
            self.update_debater_traits_widgets()
        except tk.TclError:
            # 输入无效值时恢复默认
            self.debaters_per_side_var.set(self.debaters_per_side)
    
    def on_free_debate_turns_change(self):
        """自由辩论轮数变化时的处理"""
        try:
            value = self.free_debate_turns_var.get()
            # 验证范围
            if value < 1:
                value = 1
                self.free_debate_turns_var.set(value)
            elif value > 100:
                value = 100
                self.free_debate_turns_var.set(value)
            self.free_debate_turns = value
        except tk.TclError:
            # 输入无效值时恢复默认
            self.free_debate_turns_var.set(self.free_debate_turns)
    
    def on_judges_count_change(self):
        """裁判人数变化时的处理"""
        try:
            value = self.judges_count_var.get()
            # 验证范围
            if value < 1:
                value = 1
                self.judges_count_var.set(value)
            elif value > 5:
                value = 5
                self.judges_count_var.set(value)
            self.judges_count = value
            self.update_judge_model_widgets()
        except tk.TclError:
            # 输入无效值时恢复默认
            self.judges_count_var.set(self.judges_count)
    
    def on_pro_company_change(self, event):
        """正方公司变化时的处理"""
        self.pro_company = self.pro_company_var.get()
        self.update_pro_model_options()
    
    def on_con_company_change(self, event):
        """反方公司变化时的处理"""
        self.con_company = self.con_company_var.get()
        self.update_con_model_options()
    
    def on_moderator_company_change(self, event):
        """主持人公司变化时的处理"""
        self.moderator_company = self.moderator_company_var.get()
        self.update_moderator_model_options()
    
    def update_moderator_model_options(self):
        """更新主持人模型选项"""
        # 获取当前公司的模型列表
        models = models_by_company.get(self.moderator_company, [])
        
        # 设置模型下拉菜单选项
        self.moderator_model_combobox['values'] = models
        
        # 默认选择第一个模型
        if models:
            self.moderator_model_var.set(models[0])
        else:
            self.moderator_model_var.set("")
    
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
            model_combobox = ttk.Combobox(self.pro_models_frame, textvariable=model_var, values=models, width=30, state="readonly")
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
            model_combobox = ttk.Combobox(self.con_models_frame, textvariable=model_var, values=models, width=30, state="readonly")
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
            model_combobox = ttk.Combobox(self.judges_models_frame, textvariable=model_var, values=judge_models, width=30, state="readonly")
            model_combobox.grid(row=i, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
            
            # 默认选择第一个模型
            if judge_models:
                model_var.set(judge_models[0])
            
            self.judge_models.append(model_var)
    
    def update_debater_traits_widgets(self):
        """更新辩手特质选择控件"""
        self.update_pro_traits_options()
        self.update_con_traits_options()
    
    def update_pro_traits_options(self):
        """更新正方辩手特质选项"""
        # 销毁现有特质选择控件
        for widget in self.pro_traits_frame.winfo_children():
            widget.destroy()
        
        # 获取预定义特质，加上自定义选项
        predefined_traits = get_all_trait_names()
        all_traits = predefined_traits + ["自定义"]
        
        # 创建新的特质选择控件
        self.pro_traits = []
        self.pro_custom_entries = []  # 存储自定义输入框引用
        for i in range(self.debaters_per_side_var.get()):
            # 特质标签
            trait_label = ttk.Label(self.pro_traits_frame, text=f"辩手{i+1}特质：", font=("Arial", 9, "bold"))
            trait_label.grid(row=i*2, column=0, padx=8, pady=3, sticky=tk.W)
            
            # 特质下拉框
            trait_var = tk.StringVar()
            trait_combobox = ttk.Combobox(self.pro_traits_frame, textvariable=trait_var, values=all_traits, 
                                        width=20, state="readonly", font=("Arial", 9))
            trait_combobox.grid(row=i*2, column=1, padx=8, pady=3, sticky=(tk.W, tk.E))
            
            # 默认选择第一个特质
            if predefined_traits:
                trait_var.set(predefined_traits[0])
            
            # 特质描述文本框（可编辑，选择自定义时用户直接输入）
            desc_text = tk.Text(self.pro_traits_frame, height=2, width=45, wrap=tk.WORD, 
                              font=("Arial", 8), bg="#f8f9fa", relief="solid", bd=1)
            desc_text.grid(row=i*2+1, column=0, columnspan=2, padx=20, pady=5, sticky=(tk.W, tk.E))
            
            # 显示默认特质描述
            if predefined_traits:
                trait_info = get_trait_info(predefined_traits[0])
                desc_text.insert(tk.END, trait_info.get("description", ""))
                desc_text.config(state=tk.DISABLED)  # 预定义特质不可编辑
            
            self.pro_custom_entries.append(desc_text)
            
            # 绑定特质变化事件
            def on_trait_change(event, idx=i, cb=trait_combobox, desc=desc_text):
                selected_trait = cb.get()
                desc.config(state=tk.NORMAL)
                desc.delete("1.0", tk.END)
                if selected_trait == "自定义":
                    desc.insert(tk.END, "请输入自定义特质描述...")
                    desc.config(bg="#ffffff")  # 白色背景表示可编辑
                else:
                    trait_info = get_trait_info(selected_trait)
                    desc.insert(tk.END, trait_info.get("description", ""))
                    desc.config(state=tk.DISABLED, bg="#f8f9fa")  # 灰色背景表示只读
            
            trait_combobox.bind("<<ComboboxSelected>>", on_trait_change)
            
            self.pro_traits.append(trait_var)
    
    def update_con_traits_options(self):
        """更新反方辩手特质选项"""
        # 销毁现有特质选择控件
        for widget in self.con_traits_frame.winfo_children():
            widget.destroy()
        
        # 获取预定义特质，加上自定义选项
        predefined_traits = get_all_trait_names()
        all_traits = predefined_traits + ["自定义"]
        
        # 创建新的特质选择控件
        self.con_traits = []
        self.con_custom_entries = []  # 存储自定义输入框引用
        for i in range(self.debaters_per_side_var.get()):
            # 特质标签
            trait_label = ttk.Label(self.con_traits_frame, text=f"辩手{i+1}特质：", font=("Arial", 9, "bold"))
            trait_label.grid(row=i*2, column=0, padx=8, pady=3, sticky=tk.W)
            
            # 特质下拉框
            trait_var = tk.StringVar()
            trait_combobox = ttk.Combobox(self.con_traits_frame, textvariable=trait_var, values=all_traits, 
                                        width=20, state="readonly", font=("Arial", 9))
            trait_combobox.grid(row=i*2, column=1, padx=8, pady=3, sticky=(tk.W, tk.E))
            
            # 默认选择第一个特质
            if predefined_traits:
                trait_var.set(predefined_traits[0])
            
            # 特质描述文本框（可编辑，选择自定义时用户直接输入）
            desc_text = tk.Text(self.con_traits_frame, height=2, width=45, wrap=tk.WORD, 
                              font=("Arial", 8), bg="#f8f9fa", relief="solid", bd=1)
            desc_text.grid(row=i*2+1, column=0, columnspan=2, padx=20, pady=5, sticky=(tk.W, tk.E))
            
            # 显示默认特质描述
            if predefined_traits:
                trait_info = get_trait_info(predefined_traits[0])
                desc_text.insert(tk.END, trait_info.get("description", ""))
                desc_text.config(state=tk.DISABLED)  # 预定义特质不可编辑
            
            self.con_custom_entries.append(desc_text)
            
            # 绑定特质变化事件
            def on_trait_change(event, idx=i, cb=trait_combobox, desc=desc_text):
                selected_trait = cb.get()
                desc.config(state=tk.NORMAL)
                desc.delete("1.0", tk.END)
                if selected_trait == "自定义":
                    desc.insert(tk.END, "请输入自定义特质描述...")
                    desc.config(bg="#ffffff")  # 白色背景表示可编辑
                else:
                    trait_info = get_trait_info(selected_trait)
                    desc.insert(tk.END, trait_info.get("description", ""))
                    desc.config(state=tk.DISABLED, bg="#f8f9fa")  # 灰色背景表示只读
            
            trait_combobox.bind("<<ComboboxSelected>>", on_trait_change)
            
            self.con_traits.append(trait_var)
    
    def randomize_all_traits(self):
        """一键随机化所有辩手特质"""
        predefined_traits = get_all_trait_names()
        
        # 随机化正方特质
        for i, trait_var in enumerate(self.pro_traits):
            random_trait = get_random_trait()
            trait_var.set(random_trait)
            # 更新描述文本框
            if i < len(self.pro_custom_entries):
                desc_text = self.pro_custom_entries[i]
                desc_text.config(state=tk.NORMAL)
                desc_text.delete("1.0", tk.END)
                trait_info = get_trait_info(random_trait)
                desc_text.insert(tk.END, trait_info.get("description", ""))
                desc_text.config(state=tk.DISABLED, bg="#f8f9fa")
        
        # 随机化反方特质
        for i, trait_var in enumerate(self.con_traits):
            random_trait = get_random_trait()
            trait_var.set(random_trait)
            # 更新描述文本框
            if i < len(self.con_custom_entries):
                desc_text = self.con_custom_entries[i]
                desc_text.config(state=tk.NORMAL)
                desc_text.delete("1.0", tk.END)
                trait_info = get_trait_info(random_trait)
                desc_text.insert(tk.END, trait_info.get("description", ""))
                desc_text.config(state=tk.DISABLED, bg="#f8f9fa")
    
    def get_trait_with_description(self, traits_list, custom_entries, side):
        """获取特质及其描述，处理自定义特质"""
        result = []
        for i, trait_var in enumerate(traits_list):
            trait_name = trait_var.get()
            if trait_name == "自定义":
                # 获取自定义描述
                custom_desc = custom_entries[i].get("1.0", tk.END).strip()
                if custom_desc == "请输入自定义特质描述..." or not custom_desc:
                    custom_desc = "默认辩论风格"
                result.append({"name": "自定义", "description": custom_desc})
            else:
                result.append({"name": trait_name, "description": None})
        return result
    
    def save_config(self):
        """保存配置"""
        self.result = {
            "debaters_per_side": self.debaters_per_side_var.get(),
            "free_debate_turns": self.free_debate_turns_var.get(),
            "judges_count": self.judges_count_var.get(),
            "pro_company": self.pro_company_var.get(),
            "pro_models": [var.get() for var in self.pro_models],
            "pro_traits": self.get_trait_with_description(self.pro_traits, self.pro_custom_entries, "pro"),
            "con_company": self.con_company_var.get(),
            "con_models": [var.get() for var in self.con_models],
            "con_traits": self.get_trait_with_description(self.con_traits, self.con_custom_entries, "con"),
            "judge_models": [var.get() for var in self.judge_models],
            "moderator_company": self.moderator_company_var.get(),
            "moderator_model": self.moderator_model_var.get()
        }
        self.unbind_mousewheel()
        self.window.destroy()
    
    def cancel_config(self):
        """取消配置"""
        self.result = None
        self.unbind_mousewheel()
        self.window.destroy()
    
    def on_window_close(self):
        """窗口关闭事件处理"""
        self.result = None
        self.unbind_mousewheel()
        self.window.destroy()
    
    def unbind_mousewheel(self):
        """解除鼠标滚轮绑定"""
        try:
            self.main_canvas.unbind_all("<MouseWheel>")
        except:
            pass

class DebateUI:
    """辩论界面类"""
    
    # 颜色定义
    COLORS = {
        'pro': {'normal': '#3498db', 'active': '#00ff88', 'glow': '#00ff88'},
        'con': {'normal': '#e74c3c', 'active': '#00ff88', 'glow': '#00ff88'},
        'moderator': {'normal': '#9b59b6', 'active': '#00ff88', 'glow': '#00ff88'},
        'judge': {'normal': '#f39c12', 'active': '#00ff88', 'glow': '#00ff88'},
        'bg': '#1a1a2e',
        'panel_bg': '#16213e',
        'text_bg': '#f8f9fa',
        'stage_bg': '#0f3460',
    }
    
    def __init__(self, debate_func):
        self.debate_func = debate_func
        self.root = tk.Tk()
        self.root.title("AI辩论系统")
        self.root.geometry("1500x950")
        self.root.resizable(True, True)
        self.root.configure(bg=self.COLORS['bg'])
        
        # 消息队列
        self.message_queue = queue.Queue()
        
        # 当前发言者
        self.current_speaker = None
        
        # 辩论历史记录
        self.debate_history = []
        
        # 辩手数量（初始化后会更新）
        self.debaters_per_side = 0
        self.judges_count = 0
        
        # 是否已初始化配置
        self.is_configured = False
        
        # 辩手圆圈引用
        self.pro_circles = []
        self.con_circles = []
        self.judge_circles = []
        self.moderator_circle = None
        
        # 创建界面布局
        self.create_widgets()
        
        # 启动消息处理
        self.root.after(100, self.process_messages)
        
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = tk.Frame(self.root, bg=self.COLORS['bg'], padx=20, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ========== 顶部：辩题和控制按钮 ==========
        top_frame = tk.Frame(main_frame, bg=self.COLORS['bg'])
        top_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 辩题
        topic_label = tk.Label(top_frame, text="辩题：", font=("Microsoft YaHei", 14, "bold"),
                              bg=self.COLORS['bg'], fg='white')
        topic_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.topic_var = tk.StringVar()
        self.topic_entry = tk.Entry(top_frame, textvariable=self.topic_var, font=("Microsoft YaHei", 12),
                                   bg='white', relief='flat', width=70)
        self.topic_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10, padx=(0, 30))
        self.topic_entry.insert(0, "人工智能将更多地造福人类而非伤害人类")
        
        # 按钮
        btn_style = {'font': ("Microsoft YaHei", 11, "bold"), 'width': 12, 'relief': 'flat', 'cursor': 'hand2', 'bd': 0}
        
        self.init_config_button = tk.Button(top_frame, text="初始化配置", bg='#3498db', fg='white',
                                           activebackground='#2980b9', command=self.init_config, **btn_style)
        self.init_config_button.pack(side=tk.LEFT, padx=8, ipady=8)
        
        self.start_button = tk.Button(top_frame, text="开始辩论", bg='#27ae60', fg='white',
                                     activebackground='#219a52', command=self.start_debate,
                                     state=tk.DISABLED, **btn_style)
        self.start_button.pack(side=tk.LEFT, padx=8, ipady=8)
        
        self.restart_button = tk.Button(top_frame, text="重新开始", bg='#e74c3c', fg='white',
                                       activebackground='#c0392b', command=self.restart_debate,
                                       state=tk.DISABLED, **btn_style)
        self.restart_button.pack(side=tk.LEFT, padx=8, ipady=8)
        
        # ========== 中间区域 ==========
        middle_frame = tk.Frame(main_frame, bg=self.COLORS['bg'])
        middle_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧：辩论舞台
        left_frame = tk.Frame(middle_frame, bg=self.COLORS['bg'])
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        # 主持人发言区（顶部）
        mod_frame = tk.LabelFrame(left_frame, text="📢 主持人", font=("Microsoft YaHei", 11, "bold"),
                                 bg=self.COLORS['panel_bg'], fg='#9b59b6', labelanchor='nw')
        mod_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.moderator_text = scrolledtext.ScrolledText(mod_frame, wrap=tk.WORD, height=4,
                                                        font=("Microsoft YaHei", 10),
                                                        bg=self.COLORS['text_bg'], state=tk.DISABLED,
                                                        relief='flat')
        self.moderator_text.pack(fill=tk.X, padx=8, pady=8)
        
        # 舞台Canvas - 用于绘制辩手圆圈
        stage_container = tk.Frame(left_frame, bg=self.COLORS['stage_bg'], relief='ridge', bd=2)
        stage_container.pack(fill=tk.X, pady=10)
        
        self.stage_canvas = tk.Canvas(stage_container, bg=self.COLORS['stage_bg'], 
                                      highlightthickness=0, height=180)
        self.stage_canvas.pack(fill=tk.X, padx=5, pady=5)
        
        # 绑定窗口大小变化事件
        self.stage_canvas.bind('<Configure>', self.on_stage_resize)
        
        # 初始显示提示
        self.show_stage_placeholder()
        
        # 正反方发言区
        debate_frame = tk.Frame(left_frame, bg=self.COLORS['bg'])
        debate_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # 正方发言区
        pro_frame = tk.LabelFrame(debate_frame, text="🔵 正方发言", font=("Microsoft YaHei", 11, "bold"),
                                 bg=self.COLORS['panel_bg'], fg='#3498db', labelanchor='nw')
        pro_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        
        self.pro_speaker_label = tk.Label(pro_frame, text="等待发言...", 
                                         font=("Microsoft YaHei", 10, "bold"),
                                         bg='#3498db', fg='white', pady=6)
        self.pro_speaker_label.pack(fill=tk.X, padx=5, pady=(5, 0))
        
        self.pro_text = scrolledtext.ScrolledText(pro_frame, wrap=tk.WORD, height=10,
                                                  font=("Microsoft YaHei", 10),
                                                  bg=self.COLORS['text_bg'], state=tk.DISABLED,
                                                  relief='flat')
        self.pro_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # 反方发言区
        con_frame = tk.LabelFrame(debate_frame, text="🔴 反方发言", font=("Microsoft YaHei", 11, "bold"),
                                 bg=self.COLORS['panel_bg'], fg='#e74c3c', labelanchor='nw')
        con_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0))
        
        self.con_speaker_label = tk.Label(con_frame, text="等待发言...", 
                                         font=("Microsoft YaHei", 10, "bold"),
                                         bg='#e74c3c', fg='white', pady=6)
        self.con_speaker_label.pack(fill=tk.X, padx=5, pady=(5, 0))
        
        self.con_text = scrolledtext.ScrolledText(con_frame, wrap=tk.WORD, height=10,
                                                  font=("Microsoft YaHei", 10),
                                                  bg=self.COLORS['text_bg'], state=tk.DISABLED,
                                                  relief='flat')
        self.con_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # 裁判发言区（底部）
        judge_frame = tk.LabelFrame(left_frame, text="⚖️ 裁判评判", font=("Microsoft YaHei", 11, "bold"),
                                   bg=self.COLORS['panel_bg'], fg='#f39c12', labelanchor='nw')
        judge_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.judges_text = scrolledtext.ScrolledText(judge_frame, wrap=tk.WORD, height=4,
                                                     font=("Microsoft YaHei", 10),
                                                     bg=self.COLORS['text_bg'], state=tk.DISABLED,
                                                     relief='flat')
        self.judges_text.pack(fill=tk.X, padx=8, pady=8)
        
        # 右侧：辩论历史
        right_frame = tk.LabelFrame(middle_frame, text="📜 辩论历史", font=("Microsoft YaHei", 12, "bold"),
                                   bg=self.COLORS['panel_bg'], fg='white', labelanchor='nw', width=420)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH)
        right_frame.pack_propagate(False)
        
        self.history_text = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD,
                                                      font=("Microsoft YaHei", 9),
                                                      bg=self.COLORS['text_bg'], relief='flat')
        self.history_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=(8, 5))
        
        # 导出按钮
        self.export_button = tk.Button(right_frame, text="📥 导出本场辩论", 
                                       font=("Microsoft YaHei", 10, "bold"), bg='#6c5ce7', fg='white',
                                       activebackground='#5b4cdb', relief='flat',
                                       command=self.export_debate, cursor='hand2')
        self.export_button.pack(pady=10, ipadx=15, ipady=6)
    
    def show_stage_placeholder(self):
        """显示舞台占位提示"""
        self.stage_canvas.delete("all")
        width = self.stage_canvas.winfo_width()
        height = self.stage_canvas.winfo_height()
        if width < 10:
            width = 800
        if height < 10:
            height = 180
        
        # 显示提示文字
        self.stage_canvas.create_text(width // 2, height // 2, 
                                      text="👆 请先点击「初始化配置」按钮配置辩论参数 👆",
                                      font=("Microsoft YaHei", 14), fill='#7f8c8d')
    
    def draw_stage(self):
        """绘制辩论舞台（辩手圆圈）"""
        if not self.is_configured:
            self.show_stage_placeholder()
            return
            
        self.stage_canvas.delete("all")
        
        width = self.stage_canvas.winfo_width()
        height = self.stage_canvas.winfo_height()
        
        if width < 10:
            return
        
        # 圆圈半径 - 更大
        radius = min(35, height // 4)
        
        # 绘制中心分隔线
        self.stage_canvas.create_line(width // 2, 10, width // 2, height - 10, 
                                      fill='#4a5568', width=2, dash=(5, 3))
        
        # 绘制标签
        self.stage_canvas.create_text(width // 4, 25, text="🔵 正方", 
                                      font=("Microsoft YaHei", 14, "bold"), fill='#3498db')
        self.stage_canvas.create_text(width // 2, 25, text="⚔️ VS ⚔️", 
                                      font=("Microsoft YaHei", 16, "bold"), fill='#ffd700')
        self.stage_canvas.create_text(3 * width // 4, 25, text="反方 🔴", 
                                      font=("Microsoft YaHei", 14, "bold"), fill='#e74c3c')
        
        # 主持人圆圈（中间上方位置）
        mod_x, mod_y = width // 2, 70
        self.moderator_circle = self.draw_circle(mod_x, mod_y, radius - 8, 
                                                  self.COLORS['moderator']['normal'], "主持")
        
        # 绘制正方辩手圆圈
        self.pro_circles = []
        y_pos = 130
        if self.debaters_per_side > 0:
            pro_spacing = (width // 2 - 80) // (self.debaters_per_side + 1)
            for i in range(self.debaters_per_side):
                x = 60 + pro_spacing * (i + 1)
                circle = self.draw_circle(x, y_pos, radius, self.COLORS['pro']['normal'], f"正{i+1}")
                self.pro_circles.append(circle)
        
        # 绘制反方辩手圆圈
        self.con_circles = []
        if self.debaters_per_side > 0:
            con_spacing = (width // 2 - 80) // (self.debaters_per_side + 1)
            for i in range(self.debaters_per_side):
                x = width // 2 + 40 + con_spacing * (i + 1)
                circle = self.draw_circle(x, y_pos, radius, self.COLORS['con']['normal'], f"反{i+1}")
                self.con_circles.append(circle)
        
        # 绘制裁判圆圈（底部居中）
        self.judge_circles = []
        if self.judges_count > 0:
            judge_y = height - 30
            total_judge_width = (self.judges_count - 1) * 80
            judge_start_x = (width - total_judge_width) // 2
            for i in range(self.judges_count):
                x = judge_start_x + i * 80
                circle = self.draw_circle(x, judge_y, radius - 8, self.COLORS['judge']['normal'], f"裁{i+1}")
                self.judge_circles.append(circle)
    
    def draw_circle(self, x, y, radius, color, label):
        """绘制带标签的圆圈"""
        # 绘制外圈（用于发光效果）
        glow = self.stage_canvas.create_oval(
            x - radius - 5, y - radius - 5,
            x + radius + 5, y + radius + 5,
            fill='', outline='', width=0, tags=f"glow_{label}"
        )
        # 绘制主圆圈
        circle = self.stage_canvas.create_oval(
            x - radius, y - radius,
            x + radius, y + radius,
            fill=color, outline='white', width=3, tags=f"circle_{label}"
        )
        # 绘制标签
        text = self.stage_canvas.create_text(
            x, y, text=label, font=("Microsoft YaHei", 10, "bold"), fill='white', tags=f"text_{label}"
        )
        return {'glow': glow, 'circle': circle, 'text': text, 'x': x, 'y': y, 'radius': radius}
    
    def on_stage_resize(self, event):
        """舞台大小变化时重绘"""
        self.draw_stage()
    
    def highlight_speaker(self, speaker_name):
        """高亮当前发言者"""
        # 先重置所有圆圈颜色
        self.reset_all_circles()
        
        # 根据发言者类型高亮
        if speaker_name == "主持人" and self.moderator_circle:
            self.set_circle_glow(self.moderator_circle, self.COLORS['moderator']['active'])
        elif speaker_name.startswith("正方辩手"):
            try:
                idx = int(speaker_name[-1]) - 1
                if 0 <= idx < len(self.pro_circles):
                    self.set_circle_glow(self.pro_circles[idx], self.COLORS['pro']['active'])
            except:
                pass
        elif speaker_name.startswith("反方辩手"):
            try:
                idx = int(speaker_name[-1]) - 1
                if 0 <= idx < len(self.con_circles):
                    self.set_circle_glow(self.con_circles[idx], self.COLORS['con']['active'])
            except:
                pass
        elif speaker_name.startswith("裁判"):
            try:
                idx = int(speaker_name[-1]) - 1
                if 0 <= idx < len(self.judge_circles):
                    self.set_circle_glow(self.judge_circles[idx], self.COLORS['judge']['active'])
            except:
                pass
    
    def set_circle_glow(self, circle_data, color):
        """设置圆圈发光效果"""
        if not circle_data:
            return
        
        # 更新圆圈颜色
        self.stage_canvas.itemconfig(circle_data['circle'], fill=color, outline='#ffffff', width=4)
        
        # 添加发光效果
        x, y, r = circle_data['x'], circle_data['y'], circle_data['radius']
        self.stage_canvas.coords(circle_data['glow'], 
                                 x - r - 8, y - r - 8, x + r + 8, y + r + 8)
        self.stage_canvas.itemconfig(circle_data['glow'], outline=color, width=6)
    
    def reset_all_circles(self):
        """重置所有圆圈颜色"""
        # 主持人
        if self.moderator_circle:
            self.stage_canvas.itemconfig(self.moderator_circle['circle'], 
                                         fill=self.COLORS['moderator']['normal'], outline='white', width=3)
            self.stage_canvas.itemconfig(self.moderator_circle['glow'], outline='', width=0)
        
        # 正方
        for circle in self.pro_circles:
            self.stage_canvas.itemconfig(circle['circle'], 
                                         fill=self.COLORS['pro']['normal'], outline='white', width=3)
            self.stage_canvas.itemconfig(circle['glow'], outline='', width=0)
        
        # 反方
        for circle in self.con_circles:
            self.stage_canvas.itemconfig(circle['circle'], 
                                         fill=self.COLORS['con']['normal'], outline='white', width=3)
            self.stage_canvas.itemconfig(circle['glow'], outline='', width=0)
        
        # 裁判
        for circle in self.judge_circles:
            self.stage_canvas.itemconfig(circle['circle'], 
                                         fill=self.COLORS['judge']['normal'], outline='white', width=3)
            self.stage_canvas.itemconfig(circle['glow'], outline='', width=0)
    
    def _format_trait_display(self, trait):
        """格式化特质显示"""
        if isinstance(trait, dict):
            name = trait.get("name", "未知")
            description = trait.get("description")
            if name == "自定义" and description:
                # 自定义特质，显示描述的前20个字符
                desc_preview = description[:20] + "..." if len(description) > 20 else description
                return f"自定义: {desc_preview}"
            else:
                return name
        else:
            # 旧格式，直接返回字符串
            return str(trait) if trait else "无"
    
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
            
            # 设置已配置标志
            self.is_configured = True
            
            # 更新辩手数量并重绘舞台
            self.debaters_per_side = self.config_result['debaters_per_side']
            self.judges_count = self.config_result['judges_count']
            self.draw_stage()
            
            # 清空所有文本框和历史记录
            self.clear_all_texts()
            self.debate_history.clear()
            
            # 重置发言者标签
            self.pro_speaker_label.config(text="等待发言...")
            self.con_speaker_label.config(text="等待发言...")
            
            # 启用开始辩论按钮
            self.start_button.config(state=tk.NORMAL)
            
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
            for i, (model, trait) in enumerate(zip(self.config_result['pro_models'], self.config_result.get('pro_traits', [])), 1):
                trait_display = self._format_trait_display(trait)
                config_info += f"  • 辩手{i}：{model} (特质：{trait_display})\n"
            
            config_info += "\n【反方队伍配置】\n"
            config_info += "-"*20 + "\n"
            config_info += f"所属公司：{self.config_result['con_company']}\n"
            config_info += "辩手分配：\n"
            for i, (model, trait) in enumerate(zip(self.config_result['con_models'], self.config_result.get('con_traits', [])), 1):
                trait_display = self._format_trait_display(trait)
                config_info += f"  • 辩手{i}：{model} (特质：{trait_display})\n"
            
            config_info += "\n【裁判配置】\n"
            config_info += "-"*20 + "\n"
            config_info += "裁判分配：\n"
            for i, model in enumerate(self.config_result['judge_models'], 1):
                config_info += f"  • 裁判{i}：{model}\n"
            
            config_info += "\n" + "="*50
            
            # 添加到历史记录并显示
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
        
        # 禁用所有按钮
        self.init_config_button.config(state=tk.DISABLED)
        self.start_button.config(state=tk.DISABLED)
        self.restart_button.config(state=tk.DISABLED)
        
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
        moderator_model = self.config_result["moderator_model"]
        
        # 获取特质分配
        pro_traits = self.config_result.get("pro_traits", [])
        con_traits = self.config_result.get("con_traits", [])
        
        # 在后台线程中运行辩论，传递配置参数和模型分配
        threading.Thread(
            target=self.debate_func, 
            args=(topic, self.ui_callback, debaters_per_side, judges_count, free_debate_turns, pro_models, con_models, judge_models, moderator_model, pro_traits, con_traits), 
            daemon=True
        ).start()
    
    def restart_debate(self):
        """重新开始辩论"""
        # 恢复到初始状态
        self.init_config_button.config(state=tk.NORMAL)
        self.start_button.config(state=tk.DISABLED)
        self.restart_button.config(state=tk.DISABLED)
        
        # 清空所有内容
        self.clear_all_texts()
        self.debate_history.clear()
        self.current_speaker = None
        
        # 重置发言者标签
        self.pro_speaker_label.config(text="等待发言...")
        self.con_speaker_label.config(text="等待发言...")
        
        # 重置圆圈颜色
        self.reset_all_circles()
        
        # 清除配置
        if hasattr(self, 'config_result'):
            delattr(self, 'config_result')
        
        # 重置辩手数量为默认值并重绘舞台
        self.debaters_per_side = 3
        self.judges_count = 3
        self.draw_stage()
        
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
                # 检查是否是辩论结束信号
                if speaker_name == "__DEBATE_END__":
                    self.on_debate_end()
                else:
                    self.show_message(speaker_name, message)
        except queue.Empty:
            pass
        
        # 继续监听消息
        self.root.after(100, self.process_messages)
    
    def on_debate_end(self):
        """辩论结束时的处理"""
        # 启用重新开始按钮
        self.restart_button.config(state=tk.NORMAL)
        # 添加结束提示
        end_info = "\n" + "="*50 + "\n"
        end_info += "        辩论已结束        \n"
        end_info += "="*50 + "\n"
        end_info += "点击「重新开始」按钮可以开始新的辩论\n"
        self.debate_history.append(("系统消息", end_info))
        self.update_history_text()
    
    def show_message(self, speaker_name, message):
        """在界面上显示消息"""
        # 高亮当前发言者圆圈
        self.highlight_speaker(speaker_name)
        
        self.current_speaker = speaker_name
        
        # 显示消息
        if speaker_name == "主持人":
            self.update_text_widget(self.moderator_text, message)
        elif speaker_name.startswith("正方辩手"):
            self.pro_speaker_label.config(text=speaker_name)
            self.update_text_widget(self.pro_text, message)
        elif speaker_name.startswith("反方辩手"):
            self.con_speaker_label.config(text=speaker_name)
            self.update_text_widget(self.con_text, message)
        elif speaker_name.startswith("裁判"):
            self.update_text_widget(self.judges_text, f"【{speaker_name}】\n{message}")
        
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
    
    def run(self):
        """运行界面"""
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