import os
import shutil
import webbrowser
import json
import sys
import tkinter as tk
import win32api
import win32con
import customtkinter as ctk
from customtkinter import CTk, CTkLabel, CTkButton, CTkComboBox, CTkFrame
from CTkMessagebox import CTkMessagebox

# ====================== 常量定义 ======================
AUTHOR_NAME = "安尘，WWNNL，琪诺兔"
GITHUB_URL = "https://github.com/LifeOfAc/Pixel-Composer-Chinese-Localization"
QQ_GROUP_URL = "https://qm.qq.com/q/Vu9GTC4mw8"

# 获取基础路径
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join(BASE_DIR, "assets", "app_icon.ico")

# ====================== 初始化设置 ======================
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# ====================== 核心功能函数 ======================
def get_user_path():
    """获取PixelComposer安装路径，优先读取配置文件中的自定义路径"""
    default_path = os.path.join(os.path.expanduser("~"), "AppData", "Local", "PixelComposer")
    config_file = os.path.join(default_path, "persistPreference.json")
    
    try:
        if os.path.exists(config_file):
            with open(config_file, "r", encoding="utf-8") as f:
                config_data = json.load(f)
            
            custom_path = config_data.get("path", "").strip()
            if custom_path and os.path.exists(custom_path):
                return os.path.normpath(custom_path)
    
    except Exception as e:
        print(f"路径检测异常：{str(e)}")
    
    if not os.path.exists(default_path):
        os.makedirs(default_path, exist_ok=True)
    
    return default_path

def get_user_locale_path():
    """获取Locale文件夹路径，自动创建不存在的目录"""
    locale_path = os.path.join(get_user_path(), "Locale")
    
    if not os.path.exists(locale_path):
        try:
            os.makedirs(locale_path, exist_ok=True)
        except Exception as e:
            show_error_dialog(f"无法创建语言目录：{str(e)}")
    
    return locale_path

def get_preferences_path():
    """获取Preferences文件夹路径"""
    return os.path.join(get_user_path(), "Preferences", "1171")

def get_install_location(app_reg_key="Steam App 2299510"):
    """通过注册表获取Steam版安装路径"""
    try:
        reg_path = rf"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{app_reg_key}"
        key = win32api.RegOpenKey(win32con.HKEY_LOCAL_MACHINE, reg_path, 0, win32con.KEY_READ)
        install_path, _ = win32api.RegQueryValueEx(key, "InstallLocation")
        win32api.RegCloseKey(key)
        return os.path.normpath(install_path.strip('"')) if install_path else None
    except Exception:
        return None

# ====================== 检测函数 ======================
def check_steam_installed():
    """检查是否安装了Steam版"""
    try:
        reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 2299510"
        key = win32api.RegOpenKey(win32con.HKEY_LOCAL_MACHINE, reg_path, 0, win32con.KEY_READ)
        win32api.RegCloseKey(key)
        return True
    except Exception:
        return False

def check_locale_folder_exists():
    """检查语言文件夹是否存在"""
    return os.path.exists(get_user_locale_path())

# ====================== 汉化功能函数 ======================
def modify_keys_json(locale="zh"):
    """修改keys.json文件中的语言设置"""
    keys_path = os.path.join(get_preferences_path(), "keys.json")
    try:
        with open(keys_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if data.get("local") != locale:
            data["local"] = locale
            with open(keys_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            show_success_dialog(f"汉化完成！已成功修改语言设置为 {locale}")
            return True
        else:
            show_success_dialog("汉化完成！但语言设置无需修改")
            return False
    except FileNotFoundError:
        show_error_dialog(f"未找到keys.json文件：{keys_path}")
    except json.JSONDecodeError:
        show_error_dialog("JSON文件格式错误，请检查文件内容")
    except PermissionError:
        show_error_dialog("没有文件写入权限，请用管理员权限运行")
    except Exception as e:
        show_error_dialog(str(e))
    return False

def copy_localization_folder(locale="zh"):
    """复制汉化文件夹到目标位置"""
    source_folder = os.path.join(os.getcwd(), locale)
    if not os.path.exists(source_folder):
        show_error_dialog(f"汉化文件夹 '{locale}' 未找到，请确保它在工具同目录下！")
        return

    locale_path = get_user_locale_path()
    en_folder = os.path.join(locale_path, 'en')
    target_folder = os.path.join(locale_path, locale)

    if not os.path.exists(locale_path) or not os.path.exists(en_folder):
        show_error_dialog("请检查PixelComposer安装路径！(多次尝试未果请手动安装)")
        return

    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    try:
        shutil.copytree(source_folder, target_folder, dirs_exist_ok=True)
        modify_keys_json(locale)
    except Exception as e:
        show_error_dialog(f"汉化过程中出现错误：{e}")

def delete_welcome_zip(install_path):
    """删除官方教程压缩包"""
    if not install_path:
        return "未提供有效安装路径"
    
    zip_path = os.path.join(install_path, "data", "Welcome files", "Welcome files.zip")
    if not os.path.exists(zip_path):
        return "官方英文教程压缩包不存在，可能已删除"
    
    try:
        os.remove(zip_path)
        return "成功删除官方英文教程压缩包"
    except Exception as e:
        return f"删除文件失败: {str(e)}"

def copy_tutorial_folder():
    """复制汉化教程文件夹"""
    lib_path = get_user_path()
    welcome_files_folder = os.path.join(lib_path, 'Welcome files')
    
    if not os.path.exists(lib_path) or not os.path.exists(welcome_files_folder):
        show_error_dialog("请检查PixelComposer安装路径！(多次尝试未果请手动安装)")
        return

    source_folder = os.path.join(os.getcwd(), 'Welcome files')
    if not os.path.exists(source_folder):
        show_error_dialog("汉化教程文件夹 'Welcome files' 未找到，请确保它在工具同目录下！")
        return

    try:
        # 清空目标文件夹
        for item in os.listdir(welcome_files_folder):
            item_path = os.path.join(welcome_files_folder, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
            else:
                shutil.rmtree(item_path)
        
        # 复制新内容
        shutil.copytree(source_folder, welcome_files_folder, dirs_exist_ok=True)
        show_success_dialog("教程汉化完成！")
    except Exception as e:
        show_error_dialog(f"教程汉化过程中出现错误：{e}")

def handle_tutorial_localization():
    """处理教程汉化选项"""
    msg = CTkMessagebox(
        master=root,
        title="教程清理选项",
        message="是否删除软件自动的英文教程？\n不删除会导致它在每次启动的时候，自动添加英文教程",
        icon="question",
        option_1="是",
        option_2="否",
        button_width=200,
        button_color="#FF9166",
        button_hover_color="#FF9166",
        button_text_color="#191925",
        font=("Microsoft YaHei", 14, "bold")
    )
    
    if msg.get() == "是":
        install_path = get_install_location()
        if install_path:
            result = delete_welcome_zip(install_path)
            show_info_dialog("清理结果", result)
        else:
            show_warning_dialog("路径错误", "未找到PixelComposer安装路径！")
    
    copy_tutorial_folder()

# ====================== UI工具函数 ======================
class Tooltip:
    """自定义Tooltip控件"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)
    
    def show_tip(self, event=None):
        if self.tip_window:
            return
            
        x = self.widget.winfo_rootx() + self.widget.winfo_width() + 10
        y = self.widget.winfo_rooty() - 10
        
        self.tip_window = tk.Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(True)
        self.tip_window.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(
            self.tip_window,
            text=self.text,
            background="#1a1a1a",
            foreground="#FF9166",
            relief=tk.FLAT,
            borderwidth=0,
            font=("Microsoft YaHei", 10)
        )
        label.pack()
    
    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
        self.tip_window = None

def center_window(window, width, height):
    """居中窗口位置"""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2 - 40
    window.geometry(f"{width}x{height}+{x}+{y}")

def on_window_move(event):
    """窗口移动时保持子窗口居中"""
    if event.widget == root:
        for child in [c for c in root.winfo_children() if isinstance(c, (ctk.CTkToplevel, CTkMessagebox))]:
            child.update_idletasks()
            new_x = root.winfo_rootx() + (root.winfo_width() - child.winfo_width()) // 2
            new_y = root.winfo_rooty() + (root.winfo_height() - child.winfo_height()) // 2
            child.geometry(f"+{new_x}+{new_y}")

def create_centered_dialog(parent, dialog_type, **kwargs):
    """创建居中对话框"""
    dialog = dialog_type(master=parent, **kwargs)
    dialog.update_idletasks()
    
    parent_root_x = parent.winfo_rootx()
    parent_root_y = parent.winfo_rooty()
    parent_width = parent.winfo_width()
    parent_height = parent.winfo_height()
    
    # 计算居中位置
    x = parent_root_x + (parent_width - dialog.winfo_width()) // 2
    y = parent_root_y + (parent_height - dialog.winfo_height()) // 2 - 5
    
    dialog.geometry(f"+{x}+{y}")
    return dialog

# 对话框快捷函数
def show_error_dialog(message):
    create_centered_dialog(
        root,
        CTkMessagebox,
        title="错误",
        message=message,
        icon="cancel",
        button_color="#FF9166",
        button_hover_color="#FF9166",
        button_text_color="#191925",
        font=("Microsoft YaHei", 14, "bold")
    )

def show_success_dialog(message):
    create_centered_dialog(
        root,
        CTkMessagebox,
        title="成功",
        message=message,
        icon="check",
        button_color="#FF9166",
        button_hover_color="#FF9166",
        font=("Microsoft YaHei", 14, "bold")
    )

def show_info_dialog(title, message):
    create_centered_dialog(
        root,
        CTkMessagebox,
        title=title,
        message=message,
        icon="info",
        button_color="#FF9166",
        button_hover_color="#FF9166",
        button_text_color="#191925",
        font=("Microsoft YaHei", 14, "bold")
    )

def show_warning_dialog(title, message):
    create_centered_dialog(
        root,
        CTkMessagebox,
        title=title,
        message=message,
        icon="warning",
        button_color="#FF9166",
        button_hover_color="#FF9166",
        button_text_color="#191925",
        font=("Microsoft YaHei", 14, "bold")
    )

# ====================== 主界面 ======================
def create_main_window():
    """创建主窗口界面"""
    root = CTk()
    root.geometry("500x230")
    center_window(root, 500, 230)
    root.title("PixelComposer 汉化工具")
    root.resizable(False, False)
    root.bind("<Configure>", on_window_move)
    
    # 设置窗口图标
    try:
        if os.path.exists(ICON_PATH):
            root.iconbitmap(ICON_PATH)
    except Exception:
        pass
    
    # 标题
    title_label = CTkLabel(root, text="PixelComposer 汉化工具", font=("Microsoft YaHei", 28, "bold"))
    title_label.pack(pady=10)
    
    # 输入框
    input_frame = CTkFrame(root)
    input_frame.pack(pady=5)
    
    # 改为下拉列表选择汉化包
    CTkLabel(input_frame, text="选择汉化包:", font=("Microsoft YaHei", 16)).pack(side=ctk.LEFT, padx=5)
    locale_var = ctk.StringVar(value="zh pro")
    locale_combo = CTkComboBox(
        input_frame, 
        variable=locale_var,
        values=["zh", "zh pro"],
        width=120,
        font=("Microsoft YaHei", 16, "bold"),
        dropdown_font=("Microsoft YaHei", 14),
        text_color="#FF9166",
        button_color="#FF9166",
        button_hover_color="#FF9166"
    )
    locale_combo.pack(side=ctk.LEFT, padx=5)
    
    # 功能按钮
    button_frame = CTkFrame(root)
    button_frame.pack(pady=5)
    
    CTkButton(
        button_frame,
        text="一键汉化软件",
        command=lambda: copy_localization_folder(locale_var.get().strip() or "zh"),
        width=150,
        font=("Microsoft YaHei", 14, "bold"),
        text_color="#191925",
        fg_color="#FF9166",
        hover_color="#FF9166"
    ).pack(side=ctk.LEFT, padx=5)
    
    CTkButton(
        button_frame,
        text="一键汉化教程",
        command=handle_tutorial_localization,
        width=150,
        font=("Microsoft YaHei", 14, "bold"),
        text_color="#191925",
        fg_color="#FF9166",
        hover_color="#FF9166"
    ).pack(side=ctk.LEFT, padx=5)
    
    # 社交按钮
    empty_frame = CTkFrame(root)
    empty_frame.pack(pady=5)
    
    CTkButton(
        empty_frame,
        text="加入特效交流群",
        command=lambda: webbrowser.open(QQ_GROUP_URL),
        width=150,
        font=("Microsoft YaHei", 14, "bold"),
        text_color="#191925",
        fg_color="#FF9166",
        hover_color="#FF9166"
    ).pack(pady=5)
    
    # 作者信息
    author_frame = CTkFrame(root, fg_color="transparent")
    author_frame.pack(pady=5)
    
    github_btn = CTkButton(
        author_frame,
        text="★",
        width=28,
        height=28,
        command=lambda: webbrowser.open(GITHUB_URL),
        font=("Microsoft YaHei", 20, "bold"),
        text_color="#FF9166",
        fg_color="transparent",
        hover_color="#2B2B2B"
    )
    github_btn.pack(side=ctk.LEFT, padx=(0, 5))
    Tooltip(github_btn, "打开GitHub给作者一个Star鼓励一下")
    
    CTkLabel(
        author_frame,
        text=f"作者:{AUTHOR_NAME}",
        font=("Microsoft YaHei", 16)
    ).pack(side=ctk.LEFT)
    
    return root

# ====================== 主程序 ======================
if __name__ == "__main__":
    root = create_main_window()
    
    # 显示初始环境检测
    steam_installed = check_steam_installed()
    locale_exists = check_locale_folder_exists()
    
    message = f"{'✅' if steam_installed else '❌'}检测到{'已' if steam_installed else '未'}安装PXC"
    message += f"\n{'✅' if locale_exists else '❌'}检测到语言文件夹" + \
              ("，可正常使用汉化功能" if locale_exists else "，请运行一次PixelComposer后再次打开汉化工具")
    message += "\n请保证汉化文件夹与本程序在同一目录"
    
    create_centered_dialog(
        root,
        CTkMessagebox,
        title="环境检测",
        message=message,
        icon="info" if steam_installed and locale_exists else "warning",
        button_color="#FF9166",
        button_hover_color="#FF9166",
        button_text_color="#191925",
        font=("Microsoft YaHei", 14, "bold")
    )
    
    root.mainloop()