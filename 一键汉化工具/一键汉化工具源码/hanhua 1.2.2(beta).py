
import os
import sys
import json
import shutil
import tempfile
import zipfile
import webbrowser
import threading
import urllib.request
import urllib.error
from typing import Optional, Callable, Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum, auto
import tkinter as tk
import win32api
import win32con
import customtkinter as ctk
from customtkinter import CTk, CTkLabel, CTkButton, CTkComboBox, CTkFrame, CTkProgressBar
from CTkMessagebox import CTkMessagebox


# ====================== 常量定义 ======================
class Constants:
    """应用常量"""
    AUTHOR_NAME = "安尘，WWNNL，琪诺兔"
    GITHUB_URL = "https://github.com/LifeOfAc/Pixel-Composer-Chinese-Localization"
    GITHUB_API_URL = "https://api.github.com/repos/LifeOfAc/Pixel-Composer-Chinese-Localization/contents/zh"
    GITHUB_FONTS_API_URL = "https://api.github.com/repos/LifeOfAc/Pixel-Composer-Chinese-Localization/contents/zh/fonts"
    QQ_GROUP_URL = "https://qm.qq.com/q/Vu9GTC4mw8"
    
    # 获取基础路径
    @staticmethod
    def get_base_dir() -> str:
        if getattr(sys, 'frozen', False):
            return sys._MEIPASS
        return os.path.dirname(os.path.abspath(__file__))
    
    @staticmethod
    def get_app_dir() -> str:
        """获取应用程序所在目录（exe运行时为exe目录，py运行时为脚本目录）"""
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        return os.path.dirname(os.path.abspath(__file__))

    @classmethod
    def get_icon_path(cls) -> str:
        return os.path.join(cls.get_base_dir(), "assets", "app_icon.ico")


# ====================== 枚举定义 ======================
class NetworkStatus(Enum):
    """网络连接状态"""
    CHECKING = auto()
    CONNECTED = auto()
    DISCONNECTED = auto()
    ERROR = auto()


class DownloadStatus(Enum):
    """下载状态"""
    IDLE = auto()
    DOWNLOADING = auto()
    SUCCESS = auto()
    FAILED = auto()
    CANCELLED = auto()


# ====================== 数据模型 ======================
@dataclass
class NetworkState:
    """网络状态数据类"""
    status: NetworkStatus = NetworkStatus.CHECKING
    latency_ms: Optional[float] = None
    error_message: Optional[str] = None
    last_check: Optional[str] = None


@dataclass
class DownloadProgress:
    """下载进度数据类"""
    status: DownloadStatus = DownloadStatus.IDLE
    current_file: str = ""
    total_files: int = 0
    completed_files: int = 0
    progress_percent: float = 0.0
    error_message: Optional[str] = None


# ====================== 工具类 ======================
class PathManager:
    """路径管理器"""
    
    @staticmethod
    def get_user_path() -> str:
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
    
    @staticmethod
    def get_user_locale_path() -> str:
        """获取Locale文件夹路径，自动创建不存在的目录"""
        locale_path = os.path.join(PathManager.get_user_path(), "Locale")
        if not os.path.exists(locale_path):
            try:
                os.makedirs(locale_path, exist_ok=True)
            except Exception as e:
                raise RuntimeError(f"无法创建语言目录：{str(e)}")
        return locale_path
    
    @staticmethod
    def get_preferences_path() -> str:
        """获取Preferences文件夹路径"""
        return os.path.join(PathManager.get_user_path(), "preferences", "1171")
    
    @staticmethod
    def get_install_location(app_reg_key: str = "Steam App 2299510") -> Optional[str]:
        """通过注册表获取Steam版安装路径"""
        try:
            reg_path = rf"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{app_reg_key}"
            key = win32api.RegOpenKey(win32con.HKEY_LOCAL_MACHINE, reg_path, 0, win32con.KEY_READ)
            install_path, _ = win32api.RegQueryValueEx(key, "InstallLocation")
            win32api.RegCloseKey(key)
            return os.path.normpath(install_path.strip('"')) if install_path else None
        except Exception:
            return None


class RegistryChecker:
    """注册表检测器"""
    
    @staticmethod
    def check_steam_installed() -> bool:
        """检查是否安装了Steam版"""
        try:
            reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 2299510"
            key = win32api.RegOpenKey(win32con.HKEY_LOCAL_MACHINE, reg_path, 0, win32con.KEY_READ)
            win32api.RegCloseKey(key)
            return True
        except Exception:
            return False
    
    @staticmethod
    def check_locale_folder_exists() -> bool:
        """检查语言文件夹是否存在"""
        locale_path = os.path.join(PathManager.get_user_path(), "Locale")
        return os.path.exists(locale_path)


class NetworkChecker:
    """网络检测器"""
    
    def __init__(self):
        self.state = NetworkState()
    
    def check_connection(self, callback: Optional[Callable[[NetworkState], None]] = None) -> NetworkState:
        """检测GitHub连接状态"""
        import time
        
        self.state.status = NetworkStatus.CHECKING
        self.state.last_check = time.strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            start_time = time.time()
            req = urllib.request.Request(
                Constants.GITHUB_API_URL,
                headers={
                    'User-Agent': 'PixelComposer-Localization-Tool',
                    'Accept': 'application/vnd.github.v3+json'
                },
                method='HEAD'
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                latency = (time.time() - start_time) * 1000
                self.state.status = NetworkStatus.CONNECTED
                self.state.latency_ms = round(latency, 2)
                self.state.error_message = None
                
        except urllib.error.HTTPError as e:
            self.state.status = NetworkStatus.ERROR
            self.state.error_message = f"HTTP错误: {e.code}"
            
        except urllib.error.URLError as e:
            self.state.status = NetworkStatus.DISCONNECTED
            self.state.error_message = "无法连接到GitHub，请检查网络"
            
        except Exception as e:
            self.state.status = NetworkStatus.ERROR
            self.state.error_message = f"网络错误: {str(e)}"
        
        if callback:
            callback(self.state)
        
        return self.state
    
    def check_async(self, callback: Callable[[NetworkState], None]):
        """异步检测网络状态"""
        thread = threading.Thread(target=self.check_connection, args=(callback,))
        thread.daemon = True
        thread.start()


class GitHubDownloader:
    """GitHub文件下载器"""
    
    def __init__(self):
        self.progress = DownloadProgress()
        self._cancelled = False
        self._downloaded_files: List[str] = []
        self._failed_count: int = 0
    
    def cancel(self):
        """取消下载"""
        self._cancelled = True
        self.progress.status = DownloadStatus.CANCELLED
    
    def _fetch_github_dir(self, url: str) -> Tuple[bool, List[Dict]]:
        """获取 GitHub 目录内容"""
        try:
            req = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'PixelComposer-Localization-Tool',
                    'Accept': 'application/vnd.github.v3+json'
                }
            )
            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode('utf-8'))
                return True, data
        except urllib.error.HTTPError as e:
            if e.code == 403:
                return False, [{"error": "API请求过于频繁，请稍后再试"}]
            return False, [{"error": f"HTTP错误: {e.code}"}]
        except urllib.error.URLError:
            return False, [{"error": "无法连接到GitHub，请检查网络连接"}]
        except Exception as e:
            return False, [{"error": f"获取文件列表失败: {str(e)}"}]

    def get_file_list(self) -> Tuple[bool, List[Dict]]:
        """获取GitHub上zh文件夹的文件列表"""
        return self._fetch_github_dir(Constants.GITHUB_API_URL)
    
    def download_file(self, url: str, target_path: str) -> bool:
        """下载单个文件"""
        try:
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            
            req = urllib.request.Request(url, headers={
                'User-Agent': 'PixelComposer-Localization-Tool'
            })
            
            with urllib.request.urlopen(req, timeout=30) as response:
                with open(target_path, 'wb') as f:
                    f.write(response.read())
            return True
            
        except Exception:
            return False
    
    def _download_files(self, target_dir: str, get_list_fn,
                        progress_callback, subdir: str = "",
                        file_prefix: str = "", finish_msg: str = "") -> bool:
        self._cancelled = False
        self._downloaded_files = []
        self._failed_count = 0
        self.progress.status = DownloadStatus.DOWNLOADING

        success, file_list = get_list_fn()
        if not success:
            self.progress.status = DownloadStatus.FAILED
            self.progress.error_message = file_list[0].get("error", "未知错误") if file_list else "获取文件列表失败"
            if progress_callback:
                progress_callback(self.progress)
            return False

        files = [f for f in file_list if f.get("type") == "file"]
        if not files:
            self.progress.status = DownloadStatus.SUCCESS
            self.progress.progress_percent = 100.0
            if progress_callback:
                progress_callback(self.progress)
            return True

        self.progress.total_files = len(files)
        final_dir = os.path.join(target_dir, subdir) if subdir else target_dir

        for i, file_info in enumerate(files):
            if self._cancelled:
                self.progress.status = DownloadStatus.CANCELLED
                if progress_callback:
                    progress_callback(self.progress)
                return False

            filename = file_info.get("name", "")
            self.progress.current_file = f"{file_prefix}{filename}"
            self.progress.completed_files = i
            self.progress.progress_percent = (i / len(files)) * 100 if files else 0

            if progress_callback:
                progress_callback(self.progress)

            download_url = file_info.get("download_url", "")
            if download_url:
                target_path = os.path.join(final_dir, filename)
                if self.download_file(download_url, target_path):
                    self._downloaded_files.append(target_path)
                else:
                    self._failed_count += 1

        all_succeeded = self._failed_count == 0 and len(self._downloaded_files) == len(files)
        self.progress.completed_files = len(files)
        self.progress.progress_percent = 100.0
        self.progress.status = DownloadStatus.SUCCESS if all_succeeded else DownloadStatus.FAILED
        if not all_succeeded:
            self.progress.error_message = f"{self._failed_count} 个文件下载失败"
        if finish_msg:
            self.progress.current_file = finish_msg

        if progress_callback:
            progress_callback(self.progress)

        return self.progress.status == DownloadStatus.SUCCESS

    def download_all(self, target_dir: str,
                     progress_callback: Optional[Callable[[DownloadProgress], None]] = None) -> bool:
        """下载所有汉化文件"""
        return self._download_files(target_dir, self.get_file_list, progress_callback)
    
    def get_fonts_list(self) -> Tuple[bool, List[Dict]]:
        """获取GitHub上fonts文件夹的文件列表"""
        return self._fetch_github_dir(Constants.GITHUB_FONTS_API_URL)

    def download_fonts(self, target_dir: str,
                       progress_callback: Optional[Callable[[DownloadProgress], None]] = None) -> bool:
        """下载字体文件"""
        return self._download_files(target_dir, self.get_fonts_list, progress_callback,
                                    subdir="fonts", file_prefix="fonts/", finish_msg="字体下载完成")

    def download_via_zip(self, target_dir: str,
                         progress_callback: Optional[Callable[[DownloadProgress], None]] = None) -> bool:
        """通过 codeload.github.com 下载仓库 zip 并解压 zh/ 目录"""
        self._cancelled = False
        self._downloaded_files = []
        self.progress.status = DownloadStatus.DOWNLOADING

        zip_url = "https://codeload.github.com/LifeOfAc/Pixel-Composer-Chinese-Localization/zip/refs/heads/main"
        repo_prefix = "Pixel-Composer-Chinese-Localization-main/"

        tmp_path = ""
        try:
            self.progress.current_file = "通过备用线路下载..."
            self.progress.total_files = 1
            self.progress.completed_files = 0
            self.progress.progress_percent = 5
            if progress_callback:
                progress_callback(self.progress)

            req = urllib.request.Request(zip_url, headers={
                'User-Agent': 'PixelComposer-Localization-Tool'
            })

            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp:
                tmp_path = tmp.name
                with urllib.request.urlopen(req, timeout=120) as response:
                    content_length = response.headers.get('Content-Length')
                    total_size = int(content_length) if content_length else 0
                    downloaded = 0
                    while True:
                        if self._cancelled:
                            self.progress.status = DownloadStatus.CANCELLED
                            if progress_callback:
                                progress_callback(self.progress)
                            return False
                        chunk = response.read(65536)
                        if not chunk:
                            break
                        tmp.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            self.progress.progress_percent = 10 + (downloaded / total_size) * 40
                            if progress_callback:
                                progress_callback(self.progress)

            self.progress.current_file = "解压汉化文件..."
            self.progress.progress_percent = 55
            if progress_callback:
                progress_callback(self.progress)

            with zipfile.ZipFile(tmp_path, 'r') as zf:
                zh_files = [n for n in zf.namelist()
                            if n.startswith(repo_prefix + 'zh/') and not n.endswith('/')]
                if not zh_files:
                    self.progress.status = DownloadStatus.FAILED
                    self.progress.error_message = "压缩包中未找到 zh 目录"
                    if progress_callback:
                        progress_callback(self.progress)
                    return False

                self.progress.total_files = len(zh_files)
                for i, name in enumerate(zh_files):
                    if self._cancelled:
                        self.progress.status = DownloadStatus.CANCELLED
                        if progress_callback:
                            progress_callback(self.progress)
                        return False
                    relative = name[len(repo_prefix):]
                    target = os.path.join(target_dir, relative)
                    os.makedirs(os.path.dirname(target), exist_ok=True)
                    with zf.open(name) as src:
                        with open(target, 'wb') as dst:
                            dst.write(src.read())

                    self._downloaded_files.append(target)
                    self.progress.current_file = relative
                    self.progress.completed_files = i + 1
                    self.progress.progress_percent = 55 + ((i + 1) / len(zh_files)) * 45
                    if progress_callback:
                        progress_callback(self.progress)

            self.progress.completed_files = len(zh_files)
            self.progress.progress_percent = 100.0
            self.progress.status = DownloadStatus.SUCCESS if self._downloaded_files else DownloadStatus.FAILED
            self.progress.current_file = "备用线路下载完成"

            if progress_callback:
                progress_callback(self.progress)
            return self.progress.status == DownloadStatus.SUCCESS

        except urllib.error.HTTPError as e:
            self.progress.status = DownloadStatus.FAILED
            self.progress.error_message = f"备用线路 HTTP 错误: {e.code}"
            if progress_callback:
                progress_callback(self.progress)
            return False
        except Exception as e:
            self.progress.status = DownloadStatus.FAILED
            self.progress.error_message = f"备用下载失败: {str(e)}"
            if progress_callback:
                progress_callback(self.progress)
            return False
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass

    def download_with_fallback(self, target_dir: str,
                                progress_callback: Optional[Callable[[DownloadProgress], None]] = None) -> bool:
        """先 GitHub API，失败则回退 codeload zip"""
        success = self.download_all(target_dir, progress_callback)
        if success:
            return True
        if self.progress.status == DownloadStatus.CANCELLED:
            return False
        return self.download_via_zip(target_dir, progress_callback)

    def download_fonts_async(self, target_dir: str,
                             progress_callback: Optional[Callable[[DownloadProgress], None]] = None):
        """异步下载字体"""
        thread = threading.Thread(target=self.download_fonts, args=(target_dir, progress_callback))
        thread.daemon = True
        thread.start()

    def download_async(self, target_dir: str, 
                       progress_callback: Optional[Callable[[DownloadProgress], None]] = None):
        """异步下载（API 优先，自动回退备用线路）"""
        thread = threading.Thread(target=self.download_with_fallback, args=(target_dir, progress_callback))
        thread.daemon = True
        thread.start()


class LocalizationManager:
    """汉化管理器"""
    
    @staticmethod
    def modify_keys_json(locale: str = "zh") -> Tuple[bool, str]:
        """修改keys.json文件中的语言设置"""
        keys_path = os.path.join(PathManager.get_preferences_path(), "keys.json")
        
        try:
            with open(keys_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if data.get("local") != locale:
                data["local"] = locale
                with open(keys_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                return True, f"汉化完成！已成功修改语言设置为 {locale}"
            else:
                return True, "汉化完成！但语言设置无需修改"
                
        except FileNotFoundError:
            return False, f"未找到keys.json文件：{keys_path}"
        except json.JSONDecodeError:
            return False, "JSON文件格式错误，请检查文件内容"
        except PermissionError:
            return False, "没有文件写入权限，请用管理员权限运行"
        except Exception as e:
            return False, str(e)
    
    def copy_localization_folder(self, source_folder: str, locale: str = "zh") -> Tuple[bool, str]:
        """复制汉化文件夹到目标位置"""
        if not os.path.exists(source_folder):
            return False, f"汉化文件夹 '{source_folder}' 未找到！"
        
        locale_path = PathManager.get_user_locale_path()
        en_folder = os.path.join(locale_path, 'en')
        target_folder = os.path.join(locale_path, locale)
        
        if not os.path.exists(en_folder):
            return False, "请检查PixelComposer安装路径！(多次尝试未果请手动安装)"
        
        try:
            if not os.path.exists(target_folder):
                os.makedirs(target_folder)
            
            shutil.copytree(source_folder, target_folder, dirs_exist_ok=True)
            
            success, message = self.modify_keys_json(locale)
            return success, message if success else f"复制成功但{message}"
            
        except Exception as e:
            return False, f"汉化过程中出现错误：{e}"
    
    def delete_welcome_zip(self, install_path: str) -> str:
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
    
    def copy_tutorial_folder(self, source_folder: str) -> Tuple[bool, str]:
        """复制汉化教程文件夹"""
        lib_path = PathManager.get_user_path()
        welcome_files_folder = os.path.join(lib_path, 'Welcome files')
        
        if not os.path.exists(lib_path) or not os.path.exists(welcome_files_folder):
            return False, "请检查PixelComposer安装路径！(多次尝试未果请手动安装)"
        
        if not os.path.exists(source_folder):
            return False, "汉化教程文件夹 'Welcome files' 未找到！"
        
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
            return True, "教程汉化完成！"
            
        except Exception as e:
            return False, f"教程汉化过程中出现错误：{e}"


# ====================== UI组件 ======================
class StepCard(ctk.CTkFrame):
    """步骤卡片组件"""

    STATE_COLORS = {
        "pending": ("#555555", "#888888", "transparent"),
        "active":  ("#FF9166", "#FF9166", "#1E1E2E"),
        "done":    ("#4CAF50", "#4CAF50", "#1E2E1E"),
        "error":   ("#FF6B6B", "#FF6B6B", "#2E1E1E"),
    }

    def __init__(self, master, step_num: int, title: str, subtitle: str = "", **kwargs):
        super().__init__(master, corner_radius=8, border_width=1, **kwargs)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill=tk.X, padx=10, pady=(8, 0))

        self.badge = ctk.CTkLabel(
            header, text=str(step_num),
            width=26, height=26, corner_radius=13,
            fg_color="#FF9166", text_color="#191925",
            font=("Microsoft YaHei", 14, "bold")
        )
        self.badge.pack(side=tk.LEFT, padx=(0, 8))

        self.title_label = ctk.CTkLabel(
            header, text=title,
            font=("Microsoft YaHei", 16, "bold"),
            text_color="#FF9166"
        )
        self.title_label.pack(side=tk.LEFT)

        self.status_badge = ctk.CTkLabel(
            header, text="",
            font=("Microsoft YaHei", 11),
            text_color="#888888"
        )
        self.status_badge.pack(side=tk.RIGHT, padx=(5, 0))

        if subtitle:
            ctk.CTkLabel(
                self, text=subtitle,
                font=("Microsoft YaHei", 11),
                text_color="#888888"
            ).pack(anchor=tk.W, padx=10, pady=(2, 0))

        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill=tk.X, padx=10, pady=8)

        self.set_state("pending")

    def set_state(self, state: str, status_text: str = ""):
        border_color, title_color, bg_color = self.STATE_COLORS.get(
            state, self.STATE_COLORS["pending"]
        )
        self.configure(border_color=border_color, fg_color=bg_color)
        self.title_label.configure(text_color=title_color)
        if status_text:
            self.status_badge.configure(text=status_text)


class StatusBar(ctk.CTkFrame):
    """状态栏组件"""

    STATUS_COLORS = {
        NetworkStatus.CHECKING: ("#FFA500", "检测中..."),
        NetworkStatus.CONNECTED: ("#00FF00", "已连接"),
        NetworkStatus.DISCONNECTED: ("#FF0000", "未连接"),
        NetworkStatus.ERROR: ("#FF6B6B", "连接错误"),
    }

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.status_label = ctk.CTkLabel(
            self,
            text="GitHub: 检测中...",
            font=("Microsoft YaHei", 11),
            text_color="#FFA500"
        )
        self.status_label.pack(side=tk.LEFT, padx=5)

        self.latency_label = ctk.CTkLabel(
            self,
            text="",
            font=("Microsoft YaHei", 10),
            text_color="#888888"
        )
        self.latency_label.pack(side=tk.LEFT, padx=5)

        self.github_btn = ctk.CTkButton(
            self,
            text="★ GitHub",
            width=80,
            height=24,
            command=lambda: webbrowser.open(Constants.GITHUB_URL),
            font=("Microsoft YaHei", 10),
            text_color="#FF9166",
            fg_color="transparent",
            hover_color="#2B2B2B"
        )
        self.github_btn.pack(side=tk.RIGHT, padx=5)

        self.refresh_btn = ctk.CTkButton(
            self,
            text="⟳",
            width=30,
            height=24,
            command=self.on_refresh,
            font=("Microsoft YaHei", 12),
            text_color="#888888",
            fg_color="transparent",
            hover_color="#2B2B2B"
        )
        self.refresh_btn.pack(side=tk.RIGHT, padx=2)

        self.on_refresh_callback: Optional[Callable] = None

    def on_refresh(self):
        self.set_status(NetworkStatus.CHECKING)
        if self.on_refresh_callback:
            self.on_refresh_callback()

    def set_status(self, status: NetworkStatus, latency_ms: Optional[float] = None):
        color, text = self.STATUS_COLORS.get(status, ("#888888", "未知"))
        self.status_label.configure(text=f"GitHub: {text}", text_color=color)
        if latency_ms is not None and status == NetworkStatus.CONNECTED:
            self.latency_label.configure(text=f"({latency_ms}ms)")
        else:
            self.latency_label.configure(text="")


# ====================== 主控制器 ======================
class MainController:
    """主控制器"""
    
    def __init__(self):
        self.root: Optional[CTk] = None
        self.localization_manager = LocalizationManager()
        self.network_checker = NetworkChecker()
        self.github_downloader = GitHubDownloader()
        self.status_bar: Optional[StatusBar] = None
        self.locale_var: Optional[ctk.StringVar] = None
        self.locale_combo: Optional[ctk.CTkComboBox] = None
        self.cancel_btn: Optional[ctk.CTkButton] = None
        self._pending_font_download: bool = False
        self._local_source: Optional[str] = None
        self._is_downloading: bool = False

        # 卡片引用（create_main_window 中赋值）
        self.card1: Optional[StepCard] = None
        self.card2: Optional[StepCard] = None
        self.card3: Optional[StepCard] = None
        self.locale_status_label: Optional[ctk.CTkLabel] = None

        # 内嵌进度条（create_main_window 中创建）
        self.progress_frame: Optional[ctk.CTkFrame] = None
        self.download_progress_bar: Optional[ctk.CTkProgressBar] = None
        self.download_file_label: Optional[ctk.CTkLabel] = None
        self.download_status_label: Optional[ctk.CTkLabel] = None
    
    def center_window(self, window, width: int, height: int):
        """居中窗口"""
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2 - 40
        window.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_centered_dialog(self, dialog_type, **kwargs):
        """创建居中对话框"""
        dialog = dialog_type(master=self.root, **kwargs)
        dialog.update_idletasks()
        
        parent_root_x = self.root.winfo_rootx()
        parent_root_y = self.root.winfo_rooty()
        parent_width = self.root.winfo_width()
        parent_height = self.root.winfo_height()
        
        x = parent_root_x + (parent_width - dialog.winfo_width()) // 2
        y = parent_root_y + (parent_height - dialog.winfo_height()) // 2 - 5
        dialog.geometry(f"+{x}+{y}")
        return dialog
    
    def show_message(self, title: str, message: str, icon: str = "info"):
        """显示消息对话框"""
        return self.create_centered_dialog(
            CTkMessagebox,
            title=title,
            message=message,
            icon=icon,
            button_color="#FF9166",
            button_hover_color="#FF9166",
            button_text_color="#191925",
            font=("Microsoft YaHei", 14, "bold")
        )
    
    def show_error(self, message: str):
        """显示错误"""
        self.show_message("错误", message, "cancel")
    
    def show_success(self, message: str):
        """显示成功"""
        self.show_message("成功", message, "check")
    
    def show_warning(self, title: str, message: str):
        """显示警告"""
        self.create_centered_dialog(
            CTkMessagebox,
            title=title,
            message=message,
            icon="warning",
            button_color="#FF9166",
            button_hover_color="#FF9166",
            button_text_color="#191925",
            font=("Microsoft YaHei", 14, "bold")
        )
    
    def on_network_status_changed(self, state: NetworkState):
        """网络状态变更回调（工作线程调用，封送到主线程更新 UI）"""
        snapshot = NetworkState(
            status=state.status,
            latency_ms=state.latency_ms,
            error_message=state.error_message,
            last_check=state.last_check,
        )
        self.root.after(0, self._handle_network_status_changed, snapshot)

    def _handle_network_status_changed(self, state: NetworkState):
        """在主线程中更新网络状态显示"""
        if self.status_bar:
            self.status_bar.set_status(state.status, state.latency_ms)
    
    def check_network_async(self):
        """异步检测网络"""
        self.network_checker.check_async(self.on_network_status_changed)
    
    def on_download_progress(self, progress: DownloadProgress):
        """下载进度回调（工作线程调用，封送到主线程更新 UI）"""
        snapshot = DownloadProgress(
            status=progress.status,
            current_file=progress.current_file,
            total_files=progress.total_files,
            completed_files=progress.completed_files,
            progress_percent=progress.progress_percent,
            error_message=progress.error_message,
        )
        self.root.after(0, self._handle_download_progress, snapshot)

    def _handle_download_progress(self, progress: DownloadProgress):
        """在主线程中处理下载进度"""
        if self.download_progress_bar:
            self.download_progress_bar.set(progress.progress_percent / 100)
        if self.download_file_label:
            self.download_file_label.configure(text=f"正在下载: {progress.current_file}")
        if self.download_status_label:
            self.download_status_label.configure(
                text=f"{progress.completed_files}/{progress.total_files} 文件"
            )

        if progress.status == DownloadStatus.SUCCESS:
            if self._pending_font_download:
                self._pending_font_download = False
                self.github_downloader.download_fonts_async(
                    os.path.join(Constants.get_app_dir(), "zh_online"),
                    self.on_font_download_progress
                )
            else:
                self._finish_download()
        elif progress.status == DownloadStatus.FAILED:
            self.card1.set_state("error", "✗ 下载失败")
            self._is_downloading = False
            self._hide_progress()
        elif progress.status == DownloadStatus.CANCELLED:
            self._is_downloading = False
            self.card1.set_state("pending", "")
            self.card2.set_state("pending", "→ 请先获取汉化包")
            self._hide_progress()

    def _finish_download(self):
        """下载完成后的清理"""
        self._is_downloading = False
        self.card1.set_state("done", "✓ 下载完成")
        self.card2.set_state("active", "→ 准备就绪")
        self._hide_progress()

    def _hide_progress(self):
        """隐藏进度条"""
        if self.progress_frame:
            self.progress_frame.pack_forget()
        if self.cancel_btn:
            self.cancel_btn.pack_forget()

    def _show_progress(self):
        """显示进度条"""
        self._is_downloading = True
        if self.progress_frame:
            self.progress_frame.pack(fill=tk.X, pady=(8, 0))
            self.download_progress_bar.set(0)
            self.download_file_label.configure(text="准备下载...")
            self.download_status_label.configure(text="0/0 文件")
            self.cancel_btn.pack(side=tk.LEFT, padx=(6, 0))

    def _cancel_download(self):
        """取消下载"""
        self.github_downloader.cancel()

    def on_font_download_progress(self, progress: DownloadProgress):
        """字体下载进度回调（工作线程调用，封送到主线程更新 UI）"""
        snapshot = DownloadProgress(
            status=progress.status,
            current_file=progress.current_file,
            total_files=progress.total_files,
            completed_files=progress.completed_files,
            progress_percent=progress.progress_percent,
            error_message=progress.error_message,
        )
        self.root.after(0, self._handle_font_download_progress, snapshot)

    def _handle_font_download_progress(self, progress: DownloadProgress):
        """在主线程中处理字体下载进度"""
        if self.download_progress_bar:
            self.download_progress_bar.set(progress.progress_percent / 100)
        if self.download_file_label:
            self.download_file_label.configure(text=f"正在下载: {progress.current_file}")
        if self.download_status_label:
            self.download_status_label.configure(
                text=f"{progress.completed_files}/{progress.total_files} 文件"
            )

        if progress.status == DownloadStatus.SUCCESS:
            self._finish_download()
            self.show_success("汉化包及字体下载完成！")
        elif progress.status == DownloadStatus.FAILED:
            self._is_downloading = False
            self.card1.set_state("done", "✓ 下载完成 (字体失败)")
            self.card2.set_state("active", "→ 准备就绪")
            self._hide_progress()
            self.show_success("汉化包下载完成！（字体下载失败，不影响汉化功能使用）")
        elif progress.status == DownloadStatus.CANCELLED:
            self._finish_download()
    
    def download_from_github(self):
        """从GitHub下载汉化包"""
        download_dir = os.path.join(Constants.get_app_dir(), "zh_online")
        if os.path.exists(download_dir):
            shutil.rmtree(download_dir)
        self._pending_font_download = True

        self.card1.set_state("active", "下载中...")
        self._show_progress()
        self.github_downloader.download_async(download_dir, self.on_download_progress)
    
    def apply_localization(self):
        """应用汉化"""
        if self._local_source and os.path.exists(self._local_source):
            source_folder = self._local_source
            locale = os.path.basename(self._local_source)
        else:
            online_folder = os.path.join(Constants.get_app_dir(), "zh_online")
            local_folder = os.path.join(Constants.get_base_dir(), "zh")
            locale = "zh"

            if os.path.exists(online_folder) and os.listdir(online_folder):
                source_folder = online_folder
            elif os.path.exists(local_folder):
                source_folder = local_folder
            else:
                self.show_error(f"未找到汉化文件夹！\n\n请先从 GitHub 下载或选择本地文件夹。")
                return

        self.card2.set_state("active", "汉化中...")
        success, message = self.localization_manager.copy_localization_folder(source_folder, locale)
        if success:
            self.card2.set_state("done", f"✓ 已汉化 {locale}")
            self.locale_status_label.configure(text=f"状态: 已汉化 {locale}", text_color="#4CAF50")
            self.show_success(message)
        else:
            self.card2.set_state("error", "✗ 汉化失败")
            self.locale_status_label.configure(text="状态: 汉化失败", text_color="#FF6B6B")
            self.show_error(message)

    def _set_local_source(self, folder_path: str):
        """设置本地汉化文件夹路径并同步下拉框"""
        basename = os.path.basename(folder_path)
        self._local_source = folder_path
        self.locale_var.set(basename)
        self.card1.set_state("done", f"✓ 已选择: {basename}")
        self.card2.set_state("active", "→ 准备就绪")

    def _on_locale_selected(self, choice):
        """下拉框选择回调"""
        if choice == "其他...":
            from tkinter import filedialog
            folder = filedialog.askdirectory(title="选择汉化文件夹", parent=self.root)
            if folder:
                self._set_local_source(folder)
            else:
                self.locale_var.set("zh")
        elif choice == "zh":
            self._local_source = None
            online_folder = os.path.join(Constants.get_app_dir(), "zh_online")
            local_folder = os.path.join(Constants.get_base_dir(), "zh")
            if os.path.exists(online_folder) and os.listdir(online_folder):
                self.card1.set_state("done", "✓ 下载完成")
            elif os.path.exists(local_folder):
                self.card1.set_state("done", "✓ 可用本地包")
            else:
                self.card1.set_state("pending", "")

    def select_local_folder(self):
        """选择本地汉化文件夹"""
        from tkinter import filedialog
        folder = filedialog.askdirectory(title="选择汉化文件夹", parent=self.root)
        if folder:
            self._set_local_source(folder)
    
    def handle_tutorial_localization(self):
        """处理教程汉化"""
        msg = CTkMessagebox(
            master=self.root,
            title="教程清理选项",
            message="是否删除软件自带的英文教程？\n不删除会导致它在每次启动的时候，自动添加英文教程",
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
            install_path = PathManager.get_install_location()
            if install_path:
                result = self.localization_manager.delete_welcome_zip(install_path)
                self.show_message("清理结果", result)
            else:
                self.show_warning("路径错误", "未找到PixelComposer安装路径！")

        source_folder = os.path.join(Constants.get_base_dir(), 'Welcome files')
        self.card3.set_state("active", "汉化中...")
        success, message = self.localization_manager.copy_tutorial_folder(source_folder)
        if success:
            self.card3.set_state("done", "✓ 教程已汉化")
            self.show_success(message)
        else:
            self.card3.set_state("error", "✗ 失败")
            self.show_error(message)
    
    def create_main_window(self) -> CTk:
        """创建主窗口"""
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")

        self.root = CTk()
        self.root.geometry("580x480")
        self.center_window(self.root, 580, 480)
        self.root.title("PixelComposer 汉化工具 v2.0")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)

        try:
            icon_path = Constants.get_icon_path()
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception:
            pass

        self._build_header()
        self._build_card1()
        self._build_card2()
        self._build_card3()
        self._build_status_bar()

        self.card2.set_state("pending", "→ 请先获取汉化包")

        return self.root

    def _build_header(self):
        """构建顶部标题栏"""
        header_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        header_frame.pack(fill=tk.X, padx=18, pady=(12, 0))

        ctk.CTkLabel(
            header_frame, text="PixelComposer 汉化工具",
            font=("Microsoft YaHei", 22, "bold")
        ).pack(side=tk.LEFT)

        ctk.CTkLabel(
            header_frame, text=f"作者: {Constants.AUTHOR_NAME}",
            font=("Microsoft YaHei", 10), text_color="#888888"
        ).pack(side=tk.RIGHT)

        ctk.CTkFrame(self.root, height=1, fg_color="#333333").pack(
            fill=tk.X, padx=18, pady=(4, 0)
        )

    def _build_card1(self):
        """构建卡片 1: 获取汉化包"""
        self.card1 = StepCard(self.root, 1, "获取汉化包", "从 GitHub 下载或选择本地汉化文件夹")
        self.card1.pack(fill=tk.X, padx=15, pady=(8, 4))

        c1 = ctk.CTkFrame(self.card1.content_frame, fg_color="transparent")
        c1.pack(fill=tk.X)

        ctk.CTkButton(
            c1, text="从 GitHub 下载", command=self.download_from_github,
            width=150, font=("Microsoft YaHei", 12, "bold"),
            fg_color="#4CAF50", hover_color="#45A049", text_color="#FFFFFF"
        ).pack(side=tk.LEFT, padx=(0, 6))

        ctk.CTkButton(
            c1, text="选择本地文件夹", command=self.select_local_folder,
            width=130, font=("Microsoft YaHei", 12),
            fg_color="#555555", hover_color="#666666", text_color="#FFFFFF"
        ).pack(side=tk.LEFT)

        self.progress_frame = ctk.CTkFrame(self.card1.content_frame, fg_color="transparent")

        bar_frame = ctk.CTkFrame(self.progress_frame, fg_color="transparent")
        bar_frame.pack(fill=tk.X)

        self.download_progress_bar = ctk.CTkProgressBar(bar_frame, width=310)
        self.download_progress_bar.pack(side=tk.LEFT, pady=(6, 2))
        self.download_progress_bar.set(0)

        self.cancel_btn = ctk.CTkButton(
            bar_frame, text="取消", command=self._cancel_download,
            width=50, height=20, font=("Microsoft YaHei", 10),
            fg_color="#FF6B6B", hover_color="#E55555", text_color="#FFFFFF"
        )

        p_info = ctk.CTkFrame(self.progress_frame, fg_color="transparent")
        p_info.pack(fill=tk.X)
        self.download_file_label = ctk.CTkLabel(
            p_info, text="准备下载...", font=("Microsoft YaHei", 10), text_color="#888888"
        )
        self.download_file_label.pack(side=tk.LEFT)
        self.download_status_label = ctk.CTkLabel(
            p_info, text="0/0 文件", font=("Microsoft YaHei", 10), text_color="#888888"
        )
        self.download_status_label.pack(side=tk.RIGHT)

    def _build_card2(self):
        """构建卡片 2: 应用汉化"""
        self.card2 = StepCard(self.root, 2, "应用汉化", "选择汉化包并应用到 PixelComposer")
        self.card2.pack(fill=tk.X, padx=15, pady=4)

        c2 = ctk.CTkFrame(self.card2.content_frame, fg_color="transparent")
        c2.pack(fill=tk.X)

        self.locale_var = ctk.StringVar(value="zh")
        self.locale_combo = ctk.CTkComboBox(
            c2, variable=self.locale_var, values=["zh", "其他..."],
            state="readonly",
            command=self._on_locale_selected,
            width=100, font=("Microsoft YaHei", 13, "bold"),
            dropdown_font=("Microsoft YaHei", 12),
            button_color="#FF9166", text_color="#FF9166"
        )
        self.locale_combo.pack(side=tk.LEFT, padx=(0, 8))

        ctk.CTkButton(
            c2, text="一键汉化", command=self.apply_localization,
            width=100, font=("Microsoft YaHei", 12, "bold"),
            fg_color="#FF9166", hover_color="#FF9166", text_color="#191925"
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.locale_status_label = ctk.CTkLabel(
            c2, text="状态: 未操作",
            font=("Microsoft YaHei", 11), text_color="#888888"
        )
        self.locale_status_label.pack(side=tk.LEFT)

    def _build_card3(self):
        """构建卡片 3: 其他操作"""
        self.card3 = StepCard(self.root, 3, "其他操作", "")
        self.card3.pack(fill=tk.X, padx=15, pady=4)

        c3 = ctk.CTkFrame(self.card3.content_frame, fg_color="transparent")
        c3.pack(fill=tk.X)

        ctk.CTkButton(
            c3, text="汉化教程", command=self.handle_tutorial_localization,
            width=100, font=("Microsoft YaHei", 12, "bold"),
            fg_color="#FF9166", hover_color="#FF9166", text_color="#191925"
        ).pack(side=tk.LEFT, padx=(0, 6))

        ctk.CTkButton(
            c3, text="加入交流群",
            command=lambda: webbrowser.open(Constants.QQ_GROUP_URL),
            width=110, font=("Microsoft YaHei", 12, "bold"),
            fg_color="#FF9166", hover_color="#FF9166", text_color="#191925"
        ).pack(side=tk.LEFT)

    def _build_status_bar(self):
        """构建底部状态栏"""
        self.status_bar = StatusBar(self.root, fg_color="transparent")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=15, pady=8)
        self.status_bar.on_refresh_callback = self.check_network_async

    def refresh_locale_status(self):
        """启动时读取当前汉化状态"""
        keys_path = os.path.join(PathManager.get_preferences_path(), "keys.json")
        try:
            with open(keys_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            current_locale = data.get("local", "")
            if current_locale:
                self.locale_status_label.configure(
                    text=f"状态: 已汉化 {current_locale}", text_color="#4CAF50"
                )
                self.card2.set_state("done", f"✓ 当前: {current_locale}")
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            pass

    def _on_window_close(self):
        """窗口关闭确认"""
        if self._is_downloading:
            from CTkMessagebox import CTkMessagebox
            msg = self.create_centered_dialog(
                CTkMessagebox,
                title="确认退出",
                message="下载正在进行中，确定要退出吗？",
                icon="warning",
                option_1="确定退出",
                option_2="取消",
                button_width=120,
                button_color="#FF9166",
                button_hover_color="#FF9166",
                button_text_color="#191925",
                font=("Microsoft YaHei", 14, "bold")
            )
            if msg.get() == "确定退出":
                self.github_downloader.cancel()
                self.root.destroy()
        else:
            self.root.destroy()

    def run(self):
        """运行应用"""
        self.create_main_window()
        self.refresh_locale_status()
        self.check_network_async()
        self.root.mainloop()


# ====================== 程序入口 ======================
if __name__ == "__main__":
    app = MainController()
    app.run()