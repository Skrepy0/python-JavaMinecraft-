import json
import tkinter as tk
from tkinter import ttk, messagebox
from data.blocks import blocks
from data.enchantments import enchantments
from data.items import items
from data.generic import generic, operations, slot
from data.songs import songs
from data.effects import effects

rarity = {
    "默认": "", "普通": "common", "较稀有": "uncommon", "稀有": "rare", "史诗": "epic"
}
rarity_names = []
rarity_id = []
for i in rarity.keys():
    rarity_names.append(i)
for i in rarity.values():
    rarity_id.append(i)

blocks_id = []
blocks_names = []
for i in blocks.values():
    blocks_id.append(i)
for i in blocks.keys():
    blocks_names.append(i)
items_id = []
items_names = []
for i in items.values():
    items_id.append(i)
for i in items.keys():
    items_names.append(i)
enchantments_id = []
enchantments_names = []
for i in enchantments.values():
    enchantments_id.append(i)
for i in enchantments.keys():
    enchantments_names.append(i)
generic_id = []
generic_names = []
for i in generic.values():
    generic_id.append(i)
for i in generic.keys():
    generic_names.append(i)
operations_id = []
operations_name = []
for i in operations.keys():
    operations_name.append(i)
for i in operations.values():
    operations_id.append(i)
slot_id = []
slot_name = []
for i in slot.keys():
    slot_name.append(i)
for i in slot.values():
    slot_id.append(i)

all_items = items.copy()
all_items.update(blocks)
all_items_names = []
all_items_id = []
for i in all_items.keys():
    all_items_names.append(i)
for i in all_items.values():
    all_items_id.append(i)
effects_names = []
effects_id = []
for i in effects.keys():
    effects_names.append(i)

for i in effects.values():
    effects_id.append(i)

class PlaceholderEntry(ttk.Entry):
    def __init__(self, master=None, placeholder="", *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.placeholder = placeholder
        self.default_fg = self['foreground']

        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._set_placeholder)

        self._set_placeholder()

    def _clear_placeholder(self, event=None):
        if self['foreground'] == 'grey':
            self.delete(0, tk.END)
            self['foreground'] = self.default_fg

    def _set_placeholder(self, event=None):
        if not self.get():
            self.insert(0, self.placeholder)
            self['foreground'] = 'grey'


class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)

        # 创建画布和滚动条
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        # 配置画布滚动
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        # 在画布上创建窗口
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # 鼠标滚轮绑定
        self.scrollable_frame.bind("<Enter>", self._bind_mousewheel)
        self.scrollable_frame.bind("<Leave>", self._unbind_mousewheel)

        # 布局
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def _bind_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


class MinecraftCommandGenerator:
    def __init__(self, root):
        self.root = root
        self.win_hei = root.winfo_screenheight()
        self.win_wid = root.winfo_screenwidth()
        self.root.title("Minecraft 命令生成器 (Java版 24w09a+)")
        self.root.geometry(f"{self.win_wid // 2}x{self.win_hei // 2}+{self.win_wid // 4}+{self.win_hei // 4}")

        # 创建主滚动框架
        self.main_frame = ScrollableFrame(self.root)
        self.main_frame.pack(fill="both", expand=True)

        # 物品基本信息
        self.create_basic_info_frame()

        # 物品组件
        self.create_components_frame()

        # 生成按钮和输出框
        self.create_output_frame()

        # 初始化数据
        self.load_item_types()
        self.load_enchantment_types()
        self.load_attribute_modifier_types()
        # 药水效果类型
        self.effect_types = effects_names

    def create_basic_info_frame(self):
        frame = ttk.LabelFrame(self.main_frame.scrollable_frame, text="基本信息", padding=10)
        frame.pack(fill=tk.X, padx=10, pady=5)

        # 目标选择器
        ttk.Label(frame, text="目标选择器:").grid(row=0, column=0, sticky=tk.W)
        self.selector_var = tk.StringVar(value="@p")
        ttk.Combobox(frame, textvariable=self.selector_var,
                     values=["@p", "@s", "@a", "@r", "@e"]).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)

        # 物品类型选择 - 带搜索功能
        ttk.Label(frame, text="物品类型:").grid(row=1, column=0, sticky=tk.W)
        self.item_type_var = tk.StringVar()

        # 创建搜索框和组合框
        search_frame = ttk.Frame(frame)
        search_frame.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)

        # 搜索框
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var)
        search_entry.pack(side=tk.TOP, fill=tk.X)

        # 物品类型选择框
        self.item_type_combobox = ttk.Combobox(search_frame, textvariable=self.item_type_var,
                                               values=all_items_names, state="normal")
        self.item_type_combobox.pack(side=tk.TOP, fill=tk.X)
        if all_items_names:
            self.item_type_combobox.current(0)

        # 搜索功能
        def update_item_list(event=None):
            search_text = search_var.get().lower()
            if search_text:
                filtered = [name for name in all_items_names if search_text in name.lower()]
                self.item_type_combobox['values'] = filtered
                if filtered:
                    self.item_type_combobox.current(0)
            else:
                self.item_type_combobox['values'] = all_items_names
                if all_items_names:
                    self.item_type_combobox.current(0)

        search_entry.bind("<KeyRelease>", update_item_list)

        # 初始加载物品列表
        update_item_list()

        # 物品数量
        ttk.Label(frame, text="数量:").grid(row=2, column=0, sticky=tk.W)
        self.item_count_var = tk.IntVar(value=1)
        ttk.Spinbox(frame, from_=1, to=64, textvariable=self.item_count_var).grid(row=2, column=1, sticky=tk.EW, padx=5,
                                                                                  pady=2)

        frame.columnconfigure(1, weight=1)

    def create_components_frame(self):
        notebook = ttk.Notebook(self.main_frame.scrollable_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 显示属性标签页
        self.create_display_tab(notebook)

        # 附魔标签页
        self.create_enchantments_tab(notebook)
        self.create_attribute_modifier_tab(notebook)
        self.create_tool_tab(notebook)



        # 破坏/放置标签页
        self.create_block_interaction_tab(notebook)

        #食物属性
        self.create_food_tab(notebook)

        # 其他组件标签页
        self.create_other_components_tab(notebook)

    def create_display_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="显示属性")

        # 自定义名称
        ttk.Label(tab, text="自定义名称:").pack(anchor=tk.W, padx=5, pady=2)
        self.custom_name_var = tk.StringVar()
        ttk.Entry(tab, textvariable=self.custom_name_var).pack(fill=tk.X, padx=5, pady=2)

        # 是否斜体
        self.italic_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(tab, text="斜体显示", variable=self.italic_var).pack(anchor=tk.W, padx=5, pady=2)

        # 物品描述
        ttk.Label(tab, text="物品描述(每行一个):").pack(anchor=tk.W, padx=5, pady=2)
        self.lore_text = tk.Text(tab, height=5)
        self.lore_text.pack(fill=tk.X, padx=5, pady=2)

    def create_enchantments_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="附魔")

        # 添加全局"禁用附魔"复选框
        disable_frame = ttk.Frame(tab)
        disable_frame.pack(fill=tk.X, padx=5, pady=5)

        self.disable_all_enchantments_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(disable_frame, text="禁用附魔",
                        variable=self.disable_all_enchantments_var,
                        command=self.toggle_all_enchantments).pack(side=tk.LEFT)

        # 附魔列表框架
        self.enchantments_frame = ttk.LabelFrame(tab, text="附魔列表", padding=10)
        self.enchantments_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        # 添加附魔按钮
        self.add_enchant_btn = ttk.Button(tab, text="添加附魔", command=self.add_enchantment)
        self.add_enchant_btn.pack(pady=5)

        # 初始化附魔列表
        self.enchantment_widgets = []

    def create_attribute_modifier_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="属性")

        # 附魔列表
        self.attribute_modifier_frame = ttk.LabelFrame(tab, text="属性列表", padding=10)
        self.attribute_modifier_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 添加附魔按钮
        add_btn = ttk.Button(tab, text="添加属性", command=self.add_attribute_modifier)
        add_btn.pack(pady=5)

        # 初始化附魔列表
        self.attribute_modifier_widgets = []

    def create_tool_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="工具属性")
        # 创建包含复选框的框架
        checkbox_frame = ttk.Frame(tab)
        checkbox_frame.pack(anchor=tk.W, padx=5, pady=2, fill=tk.X)

        correct_for_drop_frame = ttk.Frame(checkbox_frame)
        correct_for_drop_frame.pack(fill=tk.X, pady=2)
        self.correct_for_drop_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(correct_for_drop_frame, text="是否掉落原物品", variable=self.correct_for_drop_var).pack(side=tk.LEFT)

        # 普通方块挖掘速度
        normal_frame = ttk.LabelFrame(tab, text="普通方块挖掘速度", padding=10)
        normal_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(normal_frame, text="挖掘速度倍数:").pack(side=tk.LEFT)

        # 验证函数，确保输入是正数
        def validate_speed(new_value):
            if new_value == "":
                return True
            try:
                float(new_value)
                return True
            except ValueError:
                return False

        vcmd = (tab.register(validate_speed), '%P')

        self.normal_speed_var = tk.StringVar(value="1.0")
        normal_speed_entry = ttk.Entry(normal_frame, textvariable=self.normal_speed_var,
                                       width=8, validate='key', validatecommand=vcmd)
        normal_speed_entry.pack(side=tk.LEFT, padx=5)

        # 特殊方块设置
        special_frame = ttk.LabelFrame(tab, text="特殊方块挖掘速度", padding=10)
        special_frame.pack(fill=tk.BOTH, padx=5, pady=5, expand=True)

        # 特殊方块选择（复用之前的多个方块选择逻辑）
        self.special_blocks_listbox = self._create_multi_block_selector(special_frame, "选择特殊方块")

        # 特殊方块挖掘速度
        speed_frame = ttk.Frame(special_frame)
        speed_frame.pack(fill=tk.X, pady=5)

        ttk.Label(speed_frame, text="特殊方块挖掘速度倍数:").pack(side=tk.LEFT)

        self.special_speed_var = tk.StringVar(value="1.0")
        special_speed_entry = ttk.Entry(speed_frame, textvariable=self.special_speed_var,
                                        width=8, validate='key', validatecommand=vcmd)
        special_speed_entry.pack(side=tk.LEFT, padx=5)

    def _create_multi_block_selector(self, parent, title):
        """复用之前创建的多方块选择器"""
        frame = ttk.LabelFrame(parent, text=title, padding=10)
        frame.pack(fill=tk.X, padx=5, pady=5, expand=True)

        # 已选方块列表
        selected_frame = ttk.Frame(frame)
        selected_frame.pack(fill=tk.X, pady=5)
        ttk.Label(selected_frame, text="已选方块:").pack(anchor=tk.W)

        # 创建带滚动条的列表框
        list_container = ttk.Frame(selected_frame)
        list_container.pack(fill=tk.X)

        scrollbar = ttk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        selected_blocks_listbox = tk.Listbox(
            list_container,
            height=3,
            yscrollcommand=scrollbar.set
        )
        selected_blocks_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        scrollbar.config(command=selected_blocks_listbox.yview)

        # 绑定滚轮事件，阻止事件冒泡
        def on_mousewheel(event):
            selected_blocks_listbox.yview_scroll(-1 * (event.delta // 120), "units")
            return "break"

        selected_blocks_listbox.bind("<MouseWheel>", on_mousewheel)

        # 操作按钮框架
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X)

        # 删除选中方块按钮
        remove_btn = ttk.Button(btn_frame, text="删除选中",
                                command=lambda: self.remove_selected_block(selected_blocks_listbox))
        remove_btn.pack(side=tk.LEFT, padx=2)

        # 清空列表按钮
        clear_btn = ttk.Button(btn_frame, text="清空列表",
                               command=lambda: selected_blocks_listbox.delete(0, tk.END))
        clear_btn.pack(side=tk.LEFT, padx=2)

        # 搜索和选择新方块
        search_frame = ttk.Frame(frame)
        search_frame.pack(fill=tk.X, pady=5)

        ttk.Label(search_frame, text="搜索方块:").pack(anchor=tk.W)

        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var)
        search_entry.pack(fill=tk.X, pady=2)

        # 方块选择下拉框
        cb_frame = ttk.Frame(frame)
        cb_frame.pack(fill=tk.X)

        block_var = tk.StringVar()
        cb = ttk.Combobox(cb_frame, textvariable=block_var, values=blocks_names,
                          state="readonly", width=30)
        cb.pack(side=tk.LEFT, fill=tk.X, expand=True)
        cb.current(0)

        # 添加按钮
        add_btn = ttk.Button(cb_frame, text="添加",
                             command=lambda: self.add_block_to_list(cb, selected_blocks_listbox))
        add_btn.pack(side=tk.LEFT, padx=5)

        # 搜索功能
        def update_combobox(event=None):
            search_text = search_var.get().lower()
            if search_text:
                filtered = [name for name in blocks_names if search_text in name.lower()]
                cb['values'] = filtered
                if filtered:
                    cb.current(0)
            else:
                cb['values'] = blocks_names
                cb.current(0)

        search_entry.bind("<KeyRelease>", update_combobox)

        return selected_blocks_listbox


    def create_block_interaction_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="破坏/放置")

        # 创建可添加多个方块的搜索选择组件
        def create_multi_block_selector(parent, title):
            frame = ttk.LabelFrame(parent, text=title, padding=10)
            frame.pack(fill=tk.X, padx=5, pady=5, expand=True)

            # 已选方块列表
            selected_frame = ttk.Frame(frame)
            selected_frame.pack(fill=tk.X, pady=5)
            ttk.Label(selected_frame, text="已选方块:").pack(anchor=tk.W)

            # 创建带滚动条的列表框
            list_container = ttk.Frame(selected_frame)
            list_container.pack(fill=tk.X)

            scrollbar = ttk.Scrollbar(list_container)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            selected_blocks_listbox = tk.Listbox(
                list_container,
                height=3,
                yscrollcommand=scrollbar.set
            )
            selected_blocks_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
            scrollbar.config(command=selected_blocks_listbox.yview)

            # 绑定滚轮事件，阻止事件冒泡
            def on_mousewheel(event):
                selected_blocks_listbox.yview_scroll(-1 * (event.delta // 120), "units")
                return "break"  # 阻止事件继续传播

            selected_blocks_listbox.bind("<MouseWheel>", on_mousewheel)

            # 操作按钮框架
            btn_frame = ttk.Frame(frame)
            btn_frame.pack(fill=tk.X)

            # 删除选中方块按钮
            remove_btn = ttk.Button(btn_frame, text="删除选中",
                                    command=lambda: self.remove_selected_block(selected_blocks_listbox))
            remove_btn.pack(side=tk.LEFT, padx=2)

            # 清空列表按钮
            clear_btn = ttk.Button(btn_frame, text="清空列表",
                                   command=lambda: selected_blocks_listbox.delete(0, tk.END))
            clear_btn.pack(side=tk.LEFT, padx=2)

            # 搜索和选择新方块
            search_frame = ttk.Frame(frame)
            search_frame.pack(fill=tk.X, pady=5)

            ttk.Label(search_frame, text="搜索方块:").pack(anchor=tk.W)

            search_var = tk.StringVar()
            search_entry = ttk.Entry(search_frame, textvariable=search_var)
            search_entry.pack(fill=tk.X, pady=2)

            # 方块选择下拉框
            cb_frame = ttk.Frame(frame)
            cb_frame.pack(fill=tk.X)

            block_var = tk.StringVar()
            cb = ttk.Combobox(cb_frame, textvariable=block_var, values=blocks_names,
                              state="readonly", width=30)
            cb.pack(side=tk.LEFT, fill=tk.X, expand=True)
            cb.current(0)

            # 添加按钮
            add_btn = ttk.Button(cb_frame, text="添加",
                                 command=lambda: self.add_block_to_list(cb, selected_blocks_listbox))
            add_btn.pack(side=tk.LEFT, padx=5)

            # 搜索功能
            def update_combobox(event=None):
                search_text = search_var.get().lower()
                if search_text:
                    filtered = [name for name in blocks_names if search_text in name.lower()]
                    cb['values'] = filtered
                    if filtered:
                        cb.current(0)
                else:
                    cb['values'] = blocks_names
                    cb.current(0)

            search_entry.bind("<KeyRelease>", update_combobox)

            return selected_blocks_listbox

        # 可破坏方块
        self.can_break_listbox = create_multi_block_selector(tab, "可破坏方块")

        # 可放置在方块上
        self.can_place_on_listbox = create_multi_block_selector(tab, "可放置在方块上")

    def toggle_food_options(self):
        if self.enable_food_var.get():
            self.food_options_frame.pack(fill=tk.BOTH, expand=True)
        else:
            self.food_options_frame.pack_forget()

    def add_food_effect(self):
        frame = ttk.Frame(self.effects_frame)
        frame.pack(fill=tk.X, pady=2)

        # 效果选择
        ttk.Label(frame, text="效果:").pack(side=tk.LEFT)
        effect_var = tk.StringVar()
        combobox = ttk.Combobox(frame, textvariable=effect_var, values=self.effect_types, width=20)
        combobox.pack(side=tk.LEFT, padx=5)
        combobox.current(0)

        # 等级
        ttk.Label(frame, text="等级:").pack(side=tk.LEFT)
        level_var = tk.IntVar(value=1)
        level_entry = ttk.Entry(frame, textvariable=level_var, width=3)
        level_entry.pack(side=tk.LEFT, padx=5)

        # 持续时间(秒)
        ttk.Label(frame, text="持续时间(秒):").pack(side=tk.LEFT)
        duration_var = tk.IntVar(value=30)
        duration_entry = ttk.Entry(frame, textvariable=duration_var, width=5)
        duration_entry.pack(side=tk.LEFT, padx=5)

        # 概率(0-1)
        ttk.Label(frame, text="概率(0-1):").pack(side=tk.LEFT)
        probability_var = tk.DoubleVar(value=1.0)
        probability_entry = ttk.Entry(frame, textvariable=probability_var, width=5)
        probability_entry.pack(side=tk.LEFT, padx=5)

        # 删除按钮
        remove_btn = ttk.Button(frame, text="×", width=2,
                                command=lambda f=frame: self.remove_component(f, self.food_effects))
        remove_btn.pack(side=tk.RIGHT, padx=5)

        self.food_effects.append((frame, effect_var, level_var, duration_var, probability_var))

    def create_food_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="食物属性")

        # 启用食物属性复选框
        self.enable_food_var = tk.BooleanVar(value=False)
        enable_frame = ttk.Frame(tab)
        enable_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Checkbutton(enable_frame, text="启用食物属性", variable=self.enable_food_var,
                        command=self.toggle_food_options).pack(anchor=tk.W)

        # 食物属性容器（初始隐藏）
        self.food_options_frame = ttk.Frame(tab)

        # 饱食度和饱和度
        nutrition_frame = ttk.LabelFrame(self.food_options_frame, text="营养值", padding=10)
        nutrition_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(nutrition_frame, text="饱食度:").pack(side=tk.LEFT)
        self.nutrition_var = tk.DoubleVar(value=4.0)
        nutrition_entry = ttk.Entry(nutrition_frame, textvariable=self.nutrition_var, width=5)
        nutrition_entry.pack(side=tk.LEFT, padx=5)

        ttk.Label(nutrition_frame, text="饱和度:").pack(side=tk.LEFT, padx=(10, 0))
        self.saturation_var = tk.DoubleVar(value=0.6)
        saturation_entry = ttk.Entry(nutrition_frame, textvariable=self.saturation_var, width=5)
        saturation_entry.pack(side=tk.LEFT, padx=5)

        # 进食时间和无视饱食度
        eating_frame = ttk.LabelFrame(self.food_options_frame, text="进食设置", padding=10)
        eating_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(eating_frame, text="进食时间(秒):").pack(side=tk.LEFT)
        self.eating_time_var = tk.DoubleVar(value=1.6)
        eating_time_entry = ttk.Entry(eating_frame, textvariable=self.eating_time_var, width=5)
        eating_time_entry.pack(side=tk.LEFT, padx=5)

        self.ignore_full_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(eating_frame, text="无视饱食度已满", variable=self.ignore_full_var).pack(side=tk.LEFT, padx=10)

        # 吃完后替换的物品
        replace_frame = ttk.LabelFrame(self.food_options_frame, text="吃完后替换的物品", padding=10)
        replace_frame.pack(fill=tk.BOTH, padx=5, pady=5, expand=True)

        # 添加"使用后变为其他物品"复选框
        self.use_replacement_var = tk.BooleanVar(value=False)
        replacement_check = ttk.Checkbutton(replace_frame, text="使用后变为其他物品",
                                            variable=self.use_replacement_var,
                                            command=self.toggle_replacement_options)
        replacement_check.pack(anchor=tk.W, pady=5)

        # 替换物品容器（初始隐藏）
        self.replacement_container = ttk.Frame(replace_frame)

        # 药水效果
        effects_frame = ttk.LabelFrame(self.food_options_frame, text="进食后药水效果", padding=10)
        effects_frame.pack(fill=tk.BOTH, padx=5, pady=5, expand=True)

        # 创建药水效果列表
        self.food_effects = []

        # 添加药水效果按钮
        add_effect_btn = ttk.Button(effects_frame, text="添加药水效果", command=self.add_food_effect)
        add_effect_btn.pack(anchor=tk.W, pady=5)

        # 药水效果列表容器
        self.effects_frame = ttk.Frame(effects_frame)
        self.effects_frame.pack(fill=tk.X)

        # 初始化时隐藏食物属性容器
        self.food_options_frame.pack_forget()

    def toggle_replacement_options(self):
        # 清除容器内所有内容
        for widget in self.replacement_container.winfo_children():
            widget.destroy()

        if self.use_replacement_var.get():
            self.replacement_container.pack(fill=tk.X, pady=5)

            # 替换物品搜索和选择
            search_frame = ttk.Frame(self.replacement_container)
            search_frame.pack(fill=tk.X, pady=2)

            ttk.Label(search_frame, text="替换物品:").pack(side=tk.LEFT)
            self.replacement_item_var = tk.StringVar()
            search_var = tk.StringVar()

            # 搜索框
            search_entry = ttk.Entry(search_frame, textvariable=search_var)
            search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

            # 替换物品下拉框
            cb_frame = ttk.Frame(self.replacement_container)
            cb_frame.pack(fill=tk.X)

            self.replacement_combobox = ttk.Combobox(cb_frame, textvariable=self.replacement_item_var,
                                                     values=items_names, state="readonly", width=30)
            self.replacement_combobox.pack(fill=tk.X)
            self.replacement_combobox.current(0)

            # 堆叠组件输入框
            stack_frame = ttk.Frame(self.replacement_container)
            stack_frame.pack(fill=tk.X, pady=2)

            ttk.Label(stack_frame, text="堆叠组件:").pack(side=tk.LEFT)
            self.stack_component_var = tk.StringVar()
            stack_entry = ttk.Entry(stack_frame, textvariable=self.stack_component_var)
            stack_entry.pack(fill=tk.X, expand=True, padx=5)

            # 搜索功能
            def update_combobox(event=None):
                search_text = search_var.get().lower()
                if search_text:
                    filtered = [name for name in items_names if search_text in name.lower()]
                    self.replacement_combobox['values'] = filtered
                    if filtered:
                        self.replacement_combobox.current(0)
                else:
                    self.replacement_combobox['values'] = items_names
                    self.replacement_combobox.current(0)

            search_entry.bind("<KeyRelease>", update_combobox)
        else:
            self.replacement_container.pack_forget()

    def remove_component(self, widget, widget_list):
        widget.destroy()
        for i, (w, *_) in enumerate(widget_list):
            if w == widget:
                widget_list.pop(i)
                break


    # 添加辅助方法到类中
    def add_block_to_list(self, combobox, listbox):
        block = combobox.get()

        if block and block not in listbox.get(0, tk.END) and block != blocks_names[0]:
            listbox.insert(tk.END, block)

    def remove_selected_block(self, listbox):
        selection = listbox.curselection()
        if selection:
            listbox.delete(selection[0])

    def toggle_hide_unbreakable_option(self):
        # 先清除框架内的所有内容
        for widget in self.hide_unbreakable_frame.winfo_children():
            widget.destroy()

        # 如果勾选了"不可破坏"，则添加"隐藏不可破坏"复选框
        if self.unbreakable_var.get():
            self.hide_unbreakable_text_var = tk.BooleanVar(value=False)
            ttk.Checkbutton(self.hide_unbreakable_frame, text="隐藏不可破坏",
                            variable=self.hide_unbreakable_text_var).pack(side=tk.LEFT)

    def toggle_hide_custom_model_option(self):
        # 清除之前的内容
        for widget in self.custom_model_data_input_frame.winfo_children():
            widget.destroy()

        if self.custom_model_data_var.get():
            ttk.Label(self.custom_model_data_input_frame, text="模型数据:").pack(side=tk.LEFT, padx=(5, 0))

            self.custom_amount_var = tk.DoubleVar(value=0.0)

            # 验证函数
            def validate_amount(new_value):
                try:
                    if new_value == "":
                        return True
                    float(new_value)
                    amount_entry.config(foreground='black')
                    return True
                except ValueError:
                    amount_entry.config(foreground='red')
                    return False

            vcmd = (self.custom_model_data_input_frame.register(validate_amount), '%P')
            amount_entry = ttk.Entry(self.custom_model_data_input_frame, textvariable=self.custom_amount_var, width=8,
                                     validate='key', validatecommand=vcmd)
            amount_entry.pack(side=tk.LEFT, padx=5)

    def toggle_max_durability_input(self):
        # 清除容器内所有内容
        for widget in self.max_durability_input_frame.winfo_children():
            widget.destroy()

        if self.enable_max_durability_var.get():
            ttk.Label(self.max_durability_input_frame, text="最大耐久值:").pack(side=tk.LEFT)

            self.max_durability_value_var = tk.StringVar(value="1000")

            # 验证函数，确保输入是正整数
            def validate_max_durability(new_value):
                if new_value == "":
                    return True
                try:
                    value = int(new_value)
                    if value > 0:
                        max_durability_entry.config(foreground='black')
                        return True
                    max_durability_entry.config(foreground='red')
                    return False
                except ValueError:
                    max_durability_entry.config(foreground='red')
                    return False

            vcmd = (self.max_durability_input_frame.register(validate_max_durability), '%P')
            max_durability_entry = ttk.Entry(self.max_durability_input_frame,
                                             textvariable=self.max_durability_value_var,
                                             width=8, validate='key', validatecommand=vcmd)
            max_durability_entry.pack(side=tk.LEFT)

    def toggle_max_stack_size_input(self):
        # 清除容器内所有内容
        for widget in self.max_stack_input_frame.winfo_children():
            widget.destroy()

        if self.enable_max_stack_size_var.get():
            ttk.Label(self.max_stack_input_frame, text="最大堆叠数量(不可堆叠物品慎用):").pack(side=tk.LEFT)

            self.max_stack_size_value_var = tk.StringVar(value="64")

            # 验证函数，确保输入是正整数
            def validate_max_stack_size(new_value):
                if new_value == "":
                    return True
                try:
                    value = int(new_value)
                    if value > 0:
                        max_stack_size_entry.config(foreground='black')
                        if value<100:
                            return True
                        else:
                            max_stack_size_entry.config(foreground='red')
                            return False
                    else:
                        max_stack_size_entry.config(foreground='red')
                        return False
                except ValueError:
                    max_stack_size_entry.config(foreground='red')
                    return False

            vcmd = (self.max_stack_input_frame.register(validate_max_stack_size), '%P')
            max_stack_size_entry = ttk.Entry(self.max_stack_input_frame,
                                             textvariable=self.max_stack_size_value_var,
                                             width=8, validate='key', validatecommand=vcmd)
            max_stack_size_entry.pack(side=tk.LEFT)

    def create_other_components_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="其他")

        # 创建包含复选框的框架
        checkbox_frame = ttk.Frame(tab)
        checkbox_frame.pack(anchor=tk.W, padx=5, pady=2, fill=tk.X)

        custom_model_frame = ttk.Frame(tab)
        custom_model_frame.pack(fill=tk.X, padx=5, pady=2)

        rarity_frame = ttk.Frame(tab)
        rarity_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(rarity_frame, text="物品稀有度:").pack(side=tk.LEFT)
        self.rarity_var = tk.StringVar()
        rarity_combobox = ttk.Combobox(rarity_frame, textvariable=self.rarity_var,
                                       values=rarity_names, state="readonly")
        rarity_combobox.pack(side=tk.LEFT, padx=5)
        rarity_combobox.current(0)  # 默认选择common

        # 第一行：不可破坏复选框
        unbreakable_frame = ttk.Frame(checkbox_frame)
        unbreakable_frame.pack(fill=tk.X, pady=2)
        self.unbreakable_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(unbreakable_frame, text="不可破坏", variable=self.unbreakable_var,
                        command=self.toggle_hide_unbreakable_option).pack(side=tk.LEFT)

        # 隐藏不可破坏复选框容器（初始为空）
        self.hide_unbreakable_frame = ttk.Frame(unbreakable_frame)
        self.hide_unbreakable_frame.pack(side=tk.LEFT, padx=5)

        # 第二行：其他复选框
        other_checks_frame = ttk.Frame(checkbox_frame)
        other_checks_frame.pack(fill=tk.X, pady=2)
        # 第三行：自定义模型
        self.custom_model_data_frame = ttk.Frame(checkbox_frame)
        self.custom_model_data_frame.pack(fill=tk.X, pady=2)

        # 附魔光效复选框
        self.enchantment_glint_override_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(other_checks_frame, text="附魔光效", variable=self.enchantment_glint_override_var).pack(
            side=tk.LEFT, padx=0)

        # 抗火复选框
        self.fire_resistant_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(other_checks_frame, text="抗火", variable=self.fire_resistant_var).pack(
            side=tk.LEFT, padx=5)

        # 隐藏物品提示框复选框
        self.hide_tooltip_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(other_checks_frame, text="隐藏物品提示框", variable=self.hide_tooltip_var).pack(
            side=tk.LEFT, padx=5)
        # 自定义模型复选框和输入框放在同一行

        self.custom_model_data_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(custom_model_frame, text="开启自定义模型", variable=self.custom_model_data_var,
                        command=self.toggle_hide_custom_model_option).pack(side=tk.LEFT)

        # 模型数据输入框容器
        self.custom_model_data_input_frame = ttk.Frame(custom_model_frame)
        self.custom_model_data_input_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 耐久度
        durability_frame = ttk.Frame(tab)
        durability_frame.pack(fill=tk.X, padx=5, pady=5)

        # 第一行：耐久度损耗点数
        damage_row = ttk.Frame(durability_frame)
        damage_row.pack(fill=tk.X, pady=2)

        ttk.Label(damage_row, text="耐久度损耗点数:").pack(side=tk.LEFT)

        self.damage_var = tk.StringVar(value="0")

        # 验证函数，确保输入是有效的数字
        def validate_damage_input(new_value):
            if new_value == "":
                return True
            try:
                int(new_value)
                damage_entry.config(foreground='black')
                return True
            except ValueError:
                damage_entry.config(foreground='red')
                return False

        vcmd = durability_frame.register(validate_damage_input), '%P'
        damage_entry = ttk.Entry(damage_row, textvariable=self.damage_var, width=8,
                validate='key', validatecommand=vcmd)
        damage_entry.pack(side=tk.LEFT, padx=5)

        # 第二行：最大耐久设置
        max_durability_row = ttk.Frame(durability_frame)
        max_durability_row.pack(fill=tk.X, pady=2)

        # "启用定义最大耐久"复选框
        self.enable_max_durability_var = tk.BooleanVar(value=False)
        max_durability_check = ttk.Checkbutton(max_durability_row, text="启用定义最大耐久",
                                               variable=self.enable_max_durability_var,
                                               command=self.toggle_max_durability_input)
        max_durability_check.pack(side=tk.LEFT)

        # 最大耐久输入框容器（初始隐藏）
        self.max_durability_input_frame = ttk.Frame(max_durability_row)
        self.max_durability_input_frame.pack(side=tk.LEFT, padx=5)
        #第三行设置最大堆叠数量
        max_stack_size = ttk.Frame(durability_frame)
        max_stack_size.pack(fill=tk.X, pady=3)
        # "启用定义最大堆叠数量"复选框
        self.enable_max_stack_size_var = tk.BooleanVar(value=False)
        max_durability_check = ttk.Checkbutton(max_stack_size, text="启用定义最大堆叠数量",
                                               variable=self.enable_max_stack_size_var,
                                               command=self.toggle_max_stack_size_input)
        max_durability_check.pack(side=tk.LEFT)
        # 最大堆叠数量输入框容器（初始隐藏）
        self.max_stack_input_frame = ttk.Frame(max_stack_size)
        self.max_stack_input_frame.pack(side=tk.LEFT, padx=5)

        # 可插入唱片机复选框
        self.playable_in_jukebox_var = tk.BooleanVar(value=False)
        playable_frame = ttk.Frame(tab)
        playable_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Checkbutton(playable_frame, text="可插入唱片机", variable=self.playable_in_jukebox_var,
                        command=self.toggle_jukebox_options).pack(anchor=tk.W)

        # 唱片机选项容器(初始隐藏)
        self.jukebox_options_frame = ttk.Frame(tab)

        # 歌曲搜索框
        search_frame = ttk.Frame(self.jukebox_options_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=2)

        ttk.Label(search_frame, text="搜索歌曲:").pack(side=tk.LEFT)
        self.song_search_var = tk.StringVar()
        self.song_search_entry = ttk.Entry(search_frame, textvariable=self.song_search_var)
        self.song_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.song_search_var.trace("w", self.filter_songs)

        # 歌曲选择下拉框
        ttk.Label(self.jukebox_options_frame, text="选择歌曲:").pack(anchor=tk.W, padx=5, pady=2)
        self.song_combobox = ttk.Combobox(self.jukebox_options_frame, state="readonly")
        self.song_combobox.pack(fill=tk.X, padx=5, pady=2)

        # 是否显示歌曲信息复选框（现在放在下拉框下面）
        self.show_in_tooltip_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.jukebox_options_frame, text="是否显示歌曲信息",
                        variable=self.show_in_tooltip_var).pack(anchor=tk.W, padx=5, pady=2)

        # 初始化歌曲列表
        self.songs = songs
        self.filtered_songs = self.songs.copy()
        self.update_song_combobox()  # 初始化时调用正确的方法

    def filter_songs(self, *args):
        search_term = self.song_search_var.get().lower()
        if not search_term:
            self.filtered_songs = self.songs.copy()
        else:
            self.filtered_songs = [song for song in self.songs if search_term in song.lower()]
        self.update_song_combobox()  # 确保调用的是 update_song_combobox

    def update_song_combobox(self):
        self.song_combobox['values'] = self.filtered_songs
        if self.filtered_songs:
            self.song_combobox.current(0)

    def toggle_jukebox_options(self):
        if self.playable_in_jukebox_var.get():
            self.jukebox_options_frame.pack(fill=tk.X, padx=5, pady=5)
        else:
            self.jukebox_options_frame.pack_forget()

    def create_output_frame(self):
        frame = ttk.Frame(self.main_frame.scrollable_frame)
        frame.pack(fill=tk.X, padx=10, pady=5)

        # 生成按钮
        self.generate_btn = ttk.Button(frame, text="生成命令", command=self.generate_command)
        self.generate_btn.pack(side=tk.LEFT, padx=5)

        # 复制按钮
        self.copy_btn = ttk.Button(frame, text="复制命令", command=self.copy_command)
        self.copy_btn.pack(side=tk.LEFT, padx=5)

        # 输出框
        self.output_text = tk.Text(self.main_frame.scrollable_frame, height=8, wrap=tk.WORD, font=('Consolas', 10))
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def update_damage_label(self, event=None):
        self.damage_label.config(text=f"{self.damage_var.get()}%")

    def load_item_types(self):
        item_types = all_items_names
        self.item_type_combobox['values'] = item_types
        if item_types:
            self.item_type_combobox.current(0)

    def load_enchantment_types(self):
        self.enchantment_types = enchantments_names

    def load_attribute_modifier_types(self):
        self.attribute_types = generic_names

    def toggle_all_enchantments(self):
        if self.disable_all_enchantments_var.get():
            # 隐藏附魔列表和添加按钮
            self.enchantments_frame.pack_forget()
            self.add_enchant_btn.pack_forget()
        else:
            # 显示附魔列表和添加按钮
            self.enchantments_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            self.add_enchant_btn.pack(pady=5)

    def add_enchantment(self):
        frame = ttk.Frame(self.enchantments_frame)
        frame.pack(fill=tk.X, pady=2)

        # 附魔类型选择
        enchantment_var = tk.StringVar()
        combobox = ttk.Combobox(frame, textvariable=enchantment_var, values=self.enchantment_types)
        combobox.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        if self.enchantment_types:
            combobox.current(0)

        # 附魔等级输入框
        level_frame = ttk.Frame(frame)
        level_frame.pack(side=tk.LEFT, padx=5)

        level_var = tk.IntVar(value=1)
        level_entry = ttk.Entry(level_frame, textvariable=level_var, width=5)
        level_entry.pack(side=tk.LEFT)

        # 删除按钮
        remove_btn = ttk.Button(frame, text="×", width=2,
                                command=lambda f=frame: self.remove_component(f, self.enchantment_widgets))
        remove_btn.pack(side=tk.RIGHT, padx=5)

        self.enchantment_widgets.append((frame, enchantment_var, level_var))

    def toggle_enchantment_widgets(self, frame, disabled):
        if disabled:
            frame.enchant_container.pack_forget()
        else:
            frame.enchant_container.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def add_attribute_modifier(self):
        frame = ttk.Frame(self.attribute_modifier_frame)
        frame.pack(fill=tk.X, pady=5, padx=5)

        # 属性类型选择
        ttk.Label(frame, text="属性:").pack(side=tk.LEFT, padx=(0, 5))
        attribute_var = tk.StringVar()
        attribute_cb = ttk.Combobox(frame, textvariable=attribute_var,
                                    values=self.attribute_types, width=25)
        attribute_cb.pack(side=tk.LEFT, padx=5)
        if self.attribute_types:
            attribute_cb.current(0)

        # 作用部位选择
        ttk.Label(frame, text="部位:").pack(side=tk.LEFT, padx=(10, 5))
        slot_var = tk.StringVar()
        slot_cb = ttk.Combobox(frame, textvariable=slot_var,
                               values=slot_name,
                               width=12)
        slot_cb.pack(side=tk.LEFT, padx=5)
        slot_cb.current(0)

        # 计算方式选择 - 保持原有方式不变
        ttk.Label(frame, text="计算:").pack(side=tk.LEFT, padx=(10, 5))
        operation_var = tk.StringVar()  # 保持StringVar
        operation_cb = ttk.Combobox(frame, textvariable=operation_var,
                                    values=operations_name,  # 使用原有的显示名称
                                    width=10)
        operation_cb.pack(side=tk.LEFT, padx=5)
        operation_cb.current(0)

        # 等级输入
        ttk.Label(frame, text="等级:").pack(side=tk.LEFT, padx=(10, 5))
        amount_var = tk.DoubleVar(value=0.0)

        # 验证函数
        def validate_amount(new_value):
            try:
                if new_value == "":
                    return True
                float(new_value)
                amount_entry.config(foreground='black')
                return True
            except ValueError:
                amount_entry.config(foreground='red')
                return False

        vcmd = (frame.register(validate_amount), '%P')
        amount_entry = ttk.Entry(frame, textvariable=amount_var, width=8,
                                 validate='key', validatecommand=vcmd)
        amount_entry.pack(side=tk.LEFT, padx=5)

        # 删除按钮
        remove_btn = ttk.Button(frame, text="×", width=2,
                                command=lambda f=frame: self.remove_component(f, self.attribute_modifier_widgets))
        remove_btn.pack(side=tk.RIGHT, padx=(5, 0))

        # 保存部件引用
        self.attribute_modifier_widgets.append((frame, attribute_var, slot_var, operation_var, amount_var))

    def remove_component(self, widget, widget_list):
        widget.destroy()
        for i, (w, *_) in enumerate(widget_list):
            if w == widget:
                widget_list.pop(i)
                break

    def generate_command(self):
        if not self.item_type_var.get():
            messagebox.showerror("错误", "请选择物品类型")
            return

        command = f"/give {self.selector_var.get()} {all_items[self.item_type_var.get()]}"

        # 收集所有组件
        components = []

        # 自定义名称
        if self.custom_name_var.get():
            if self.italic_var.get():
                components.append(
                    f'minecraft:custom_name="{self.custom_name_var.get()}"')
            else:
                components.append(
                    f'minecraft:item_name="{self.custom_name_var.get()}"')

        # 物品描述
        lore_lines = self.lore_text.get("1.0", tk.END).strip().split("\n")
        if lore_lines and lore_lines[0]:
            lore_json = ",".join([f'"{line}"' for line in lore_lines if line.strip()])
            components.append(f'lore=[{lore_json}]')

        # 附魔
        if self.disable_all_enchantments_var.get():
            components.append("!enchantments")
        else:
            if self.enchantment_widgets:
                enchantments_ = []
                for _, enchantment_var, level_var in self.enchantment_widgets:
                    if enchantment_var.get():
                        enchantments_.append(f'"{enchantments[enchantment_var.get()]}":{level_var.get()}')
                if enchantments_:
                    components.append(f"minecraft:enchantments={{levels:{{{','.join(enchantments_)}}}}}")

        # 属性修饰符
        if self.attribute_modifier_widgets:
            modifiers = []
            for _, attribute_var, slot_var, operation_var, amount_var in self.attribute_modifier_widgets:
                if attribute_var.get():
                    modifier = {
                        "type": f"{generic[attribute_var.get()]}",
                        "slot": slot[slot_var.get()],
                        "id": "box:1",
                        "amount": float(amount_var.get()),
                        "operation": operations[operation_var.get()]  # 直接使用英文ID
                    }
                    modifiers.append(modifier)

            if modifiers:
                modifiers_json = json.dumps(modifiers, indent=None, separators=(',', ':'))
                components.append(f"attribute_modifiers={modifiers_json}")

        # 工具属性
        tool_components = []

        # 普通方块挖掘速度
        try:
            normal_speed = float(self.normal_speed_var.get())
            if normal_speed != 1.0:  # 默认值不添加
                tool_components.append(f'default_mining_speed:{normal_speed}')
        except ValueError:
            pass

        # 特殊方块挖掘速度
        special_blocks = list(self.special_blocks_listbox.get(0, tk.END))
        if special_blocks:
            try:
                special_speed = float(self.special_speed_var.get())
                blocks_str = ",".join([f'"{blocks[b]}"' for b in special_blocks])
                if self.correct_for_drop_var.get():
                    tool_components.append(f'rules:[{{blocks:[{blocks_str}],correct_for_drops:true,speed:{special_speed}}}]')
                else:
                    tool_components.append(f'rules:[{{blocks:[{blocks_str}],correct_for_drops:false,speed:{special_speed}}}]')

            except ValueError:
                pass

        if tool_components:
            text = ",".join(tool_components)
            components.append("tool={"+text+"}")


        # 可破坏方块
        can_break_blocks = list(self.can_break_listbox.get(0, tk.END))
        if can_break_blocks:
            blocks_str = ",".join([f'"{blocks[b]}"' for b in can_break_blocks])
            components.append(f'minecraft:can_break={{predicates:[{{blocks:[{blocks_str}]}}] }}')

        # 可放置在方块上
        can_place_on_blocks = list(self.can_place_on_listbox.get(0, tk.END))
        if can_place_on_blocks:
            blocks_str = ",".join([f'"{blocks[b]}"' for b in can_place_on_blocks])
            components.append(f'minecraft:can_place_on={{predicates:[{{blocks:[{blocks_str}]}}] }}')
        #食物
        if self.enable_food_var.get():
            food_components = []

            # 营养值
            food_components.append(
                f'nutrition:{self.nutrition_var.get()},saturation:{self.saturation_var.get()}')

            # 进食时间
            if self.eating_time_var.get() != 1.6:
                food_components.append(f'eat_seconds:{self.eating_time_var.get()}')

            # 无视饱食度
            if self.ignore_full_var.get():
                food_components.append('can_always_eat:true')

            # 替换物品
            if self.use_replacement_var.get():
                replacement_item = self.replacement_item_var.get()
                stack_component = self.stack_component_var.get()

                if replacement_item:
                    if stack_component:
                        food_components.append(
                            f'using_converts_to:{{id:"{items[replacement_item]}",components:{stack_component}}}'
                        )
                    else:
                        food_components.append(
                            f'using_converts_to:{{id:"{items[replacement_item]}"}}'
                        )


            # 药水效果
            if self.food_effects:
                effects_ = []
                for _, effect_var, level_var, duration_var, probability_var in self.food_effects:
                    effects_.append(
                        f'{{effect:{{id:{effects[effect_var.get()]},amplifier:{level_var.get()},duration:{duration_var.get() * 20}}},probability:{probability_var.get()}}}'
                    )
                effects_str = ",".join(effects_)
                food_components.append(f'effects:[{effects_str}]')

            if food_components:
                text = ",".join(food_components)
                components.append("food={"+text+"}")

        # 不可破坏
        if self.unbreakable_var.get():
            if not self.hide_unbreakable_text_var.get():
                components.append("minecraft:unbreakable={}")
            else:
                components.append("minecraft:unbreakable={show_in_tooltip:false}")

        # 显示附魔光效
        if self.enchantment_glint_override_var.get():
            components.append(f"minecraft:enchantment_glint_override=true")
        # 是否抗火
        if self.fire_resistant_var.get():
            components.append("minecraft:fire_resistant={}")
        # 是否隐藏物品提示框
        if self.hide_tooltip_var.get():
            components.append("minecraft:hide_tooltip={}")
        if self.custom_model_data_var.get() and float(self.custom_amount_var.get()) != 0.0:
            components.append(f"minecraft:custom_model_data={float(self.custom_amount_var.get())}")
        # 是否插入唱片机
        if self.playable_in_jukebox_var.get() and self.song_combobox.get():
            selected_song = self.song_combobox.get()
            if not self.show_in_tooltip_var.get():
                components.append(f"jukebox_playable={{song:'{selected_song}',show_in_tooltip:false}}")
            else:
                components.append(f"jukebox_playable={{song:'{selected_song}'}}")
        # 稀有度
        if self.rarity_var.get() and self.rarity_var.get() != rarity_names[0]:  # 默认common不需要特别设置
            components.append(f'rarity="{rarity[self.rarity_var.get()]}"')

        # 耐久度
        try:
            damage_value = int(self.damage_var.get())
            if damage_value > 0:
                components.append(f"damage={damage_value}")
        except:
            pass

        # 如果启用了最大耐久定义
        if self.enable_max_durability_var.get():
            try:
                max_durability = int(self.max_durability_value_var.get())
                components.append(f"max_damage={max_durability}")
            except :
                pass
        #如果启用了定义最大堆叠数量
        if self.enable_max_stack_size_var.get():
            components.append(f"max_stack_size={int(self.max_stack_size_value_var.get())}")


        # 药水效果
        # if self.potion_effect_var.get() and self.potion_effect_var.get() != getattr(self.potion_effect_var,
        #                                                                             'placeholder', ''):
        #     components.append(f'minecraft:potion_contents={{custom_effects:[{{{self.potion_effect_var.get()}}}]}}')
        #     if self.color_var.get() and self.color_var.get() != getattr(self.color_var, 'placeholder', ''):
        #         try:
        #             rgb = int(self.color_var.get(), 16)
        #             components[-1] = components[-1][:-1] + f',custom_color:{rgb}}}'
        #         except:
        #             pass

        # 组合所有组件
        if components:
            command += f"[{','.join(components)}]"

        # 添加数量
        command += f" {self.item_count_var.get()}"

        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, command)

    def copy_command(self):
        command = self.output_text.get(1.0, tk.END).strip()
        if command:
            self.root.clipboard_clear()
            self.root.clipboard_append(command)
            messagebox.showinfo("成功", "命令已复制到剪贴板")
        else:
            messagebox.showerror("错误", "没有可复制的命令")


if __name__ == "__main__":
    root = tk.Tk()
    app = MinecraftCommandGenerator(root)
    root.mainloop()
