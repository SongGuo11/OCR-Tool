import sys
if sys.version_info < (3, 11):
    print("警告: 建议使用 Python 3.11 或更高版本")

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from screenshot_ocr import ScreenshotOCR
import keyboard

class OCRApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("OCR文字识别工具")
        # 移除固定大小
        # self.root.geometry("400x300")
        
        # 设置窗口最小尺寸
        self.root.minsize(400, 450)
        
        # 配置主窗口的网格权重，使其可以自适应
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # 添加系统托盘功能
        self.setup_tray()
        
        # 初始化变量
        self.ocr = None
        
        self.create_widgets()
        
        # 处理窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_tray(self):
        """设置系统托盘"""
        self.tray_icon = None
        try:
            import pystray
            from PIL import Image
            # 创建一个简单的图标
            icon = Image.new('RGB', (64, 64), color = 'blue')
            
            # 创建右键菜单
            menu = (
                pystray.MenuItem(
                    "显示窗口",
                    lambda: self.root.after(0, self.show_window)
                ),
                pystray.MenuItem(
                    "退出程序",
                    lambda: self.root.after(0, self.quit_app)
                )
            )
            
            self.tray_icon = pystray.Icon(
                name="OCR工具",
                icon=icon,
                title="OCR文字识别工具",
                menu=pystray.Menu(*menu)
            )
            self.tray_icon.run_detached()
        except Exception as e:
            print(f"无法创建系统托盘图标: {e}")

    def show_window(self, icon=None):
        """显示主窗口"""
        self.root.deiconify()
        self.root.lift()

    def quit_app(self):
        """完全退出程序"""
        try:
            if self.ocr:
                self.stop_service()
            if self.tray_icon:
                self.tray_icon.stop()
            self.root.destroy()  # 使用 destroy 替代 quit
            sys.exit(0)  # 确保程序完全退出
        except Exception as e:
            print(f"退出程序时出错: {e}")
            sys.exit(1)

    def on_closing(self):
        """处理窗口关闭事件"""
        message = '\n'.join([
            '您要关闭程序还是最小化到系统托盘？',
            '点击"是"关闭程序',
            '点击"否"最小化到系统托盘',
            '点击"取消"取消操作'
        ])
        
        answer = messagebox.askyesnocancel(
            title='退出程序',
            message=message,
            icon='question'
        )
        
        if answer is None:  # 取消
            return
        elif answer:  # 是，退出程序
            self.quit_app()
        else:  # 否，最小化到托盘
            self.root.withdraw()
            if self.tray_icon:
                self.tray_icon.notify(
                    '程序已最小化到系统托盘',
                    'OCR文字识别工具仍在运行'
                )

    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置主框架的网格权重
        main_frame.grid_columnconfigure(0, weight=1)
        
        # API配置区域
        api_frame = ttk.LabelFrame(main_frame, text="百度OCR配置", padding="5")
        api_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        api_frame.grid_columnconfigure(1, weight=1)  # 让输入框可以水平扩展
        
        ttk.Label(api_frame, text="APP ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.app_id_var = tk.StringVar(value='')
        self.app_id_entry = ttk.Entry(api_frame, textvariable=self.app_id_var)
        self.app_id_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        ttk.Label(api_frame, text="API Key:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.api_key_var = tk.StringVar(value='')
        self.api_key_entry = ttk.Entry(api_frame, textvariable=self.api_key_var)
        self.api_key_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        ttk.Label(api_frame, text="Secret Key:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.secret_key_var = tk.StringVar(value='')
        self.secret_key_entry = ttk.Entry(api_frame, textvariable=self.secret_key_var)
        self.secret_key_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # 快捷键设置区域
        hotkey_frame = ttk.LabelFrame(main_frame, text="快捷键设置", padding="5")
        hotkey_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        hotkey_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(hotkey_frame, text="截图快捷键:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        hotkey_input_frame = ttk.Frame(hotkey_frame)
        hotkey_input_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        
        self.hotkey_var = tk.StringVar(value='alt+d')  # 默认快捷键改为 alt+d
        self.hotkey_entry = ttk.Entry(hotkey_input_frame, textvariable=self.hotkey_var, width=15)
        self.hotkey_entry.pack(side=tk.LEFT, padx=5)
        
        self.record_button = ttk.Button(hotkey_input_frame, text='记录', width=8, command=self.record_hotkey)
        self.record_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(hotkey_frame, text='提示：点击"记录"按钮后按下组合键', foreground='gray').grid(row=1, column=0, columnspan=2, sticky=tk.W)
        
        # 控制按钮区域
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, pady=10)
        
        self.start_button = ttk.Button(control_frame, text="启动服务", width=12, command=self.start_service)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="停止服务", width=12, command=self.stop_service, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # 状态显示
        self.status_var = tk.StringVar(value="状态：未启动")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=3, column=0, pady=5)
        
        # 使用说明
        help_frame = ttk.LabelFrame(main_frame, text="使用说明", padding="5")
        help_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=5)
        help_frame.grid_columnconfigure(0, weight=1)
        
        instructions = '''1. 输入百度OCR的配置信息
2. 设置截图快捷键（默认Alt+D）
3. 点击"启动服务"按钮
4. 按快捷键进行截图识别
5. 按右键取消截图'''
        
        ttk.Label(help_frame, text=instructions, justify=tk.LEFT).grid(sticky=(tk.W, tk.E))

    def verify_baidu_ocr(self, app_id, api_key, secret_key):
        """验证百度OCR配置是否正确"""
        try:
            # 创建临时客户端测试连接
            from aip import AipOcr
            client = AipOcr(app_id, api_key, secret_key)
            
            # 尝试调用一个简单的API来验证配置
            result = client.basicGeneralUrl('https://www.baidu.com/img/flexible/logo/pc/result.png')
            
            if 'error_code' in result:
                error_msg = result.get('error_msg', '未知错误')
                messagebox.showerror("验证失败", f"API配置错误：{error_msg}")
                return False
                
            return True
            
        except Exception as e:
            messagebox.showerror("验证失败", f"无法连接到百度OCR服务：{str(e)}")
            return False

    def start_service(self):
        app_id = self.app_id_var.get()
        api_key = self.api_key_var.get()
        secret_key = self.secret_key_var.get()
        
        if not all([app_id, api_key, secret_key]):
            messagebox.showerror("错误", "请填写整的配置信息！")
            return
            
        # 验证配置
        if not self.verify_baidu_ocr(app_id, api_key, secret_key):
            return
        
        try:
            if not self.ocr:
                self.ocr = ScreenshotOCR(app_id, api_key, secret_key)
                self.ocr.init_root(self.root)
                # 使用当前设置的快捷键
                keyboard.add_hotkey(self.hotkey_var.get(), lambda: self.root.after(0, self.ocr.start_screenshot))
            
            self.status_var.set("状态：服务已启动")
            self.start_button.configure(state=tk.DISABLED)
            self.stop_button.configure(state=tk.NORMAL)
            
            messagebox.showinfo("成功", f"验证成功！服务已启动！\n按{self.hotkey_var.get()}开始截图识别")
                
        except Exception as e:
            messagebox.showerror("错误", f"启动服务失败：{str(e)}")

    def stop_service(self):
        if self.ocr:
            keyboard.remove_all_hotkeys()  # 移除所有快捷键
            self.ocr.cleanup(None)
            self.ocr = None
        self.status_var.set("状态：未启动")
        self.start_button.configure(state=tk.NORMAL)
        self.stop_button.configure(state=tk.DISABLED)

    def record_hotkey(self):
        """记录快捷键"""
        self.record_button.configure(text="请按下快捷键...", state=tk.DISABLED)
        self.root.update()
        
        keys = []
        def on_key_event(e):
            if e.event_type == keyboard.KEY_DOWN:
                if e.name not in keys and e.name not in ['left', 'right', 'up', 'down']:
                    keys.append(e.name)
            elif e.event_type == keyboard.KEY_UP:
                if len(keys) > 0:
                    # 停止记录
                    keyboard.unhook_all()
                    new_hotkey = '+'.join(keys)
                    self.hotkey_var.set(new_hotkey)
                    self.record_button.configure(text="记录快捷键", state=tk.NORMAL)
                    
                    # 如果服务已启动，更新快捷键
                    if self.ocr:
                        self.update_hotkey()
        
        keyboard.hook(on_key_event)

    def update_hotkey(self):
        """更新快捷键"""
        try:
            # 移除旧的快捷键
            keyboard.remove_all_hotkeys()
            
            # 注册新的快捷键
            hotkey = self.hotkey_var.get()
            keyboard.add_hotkey(hotkey, lambda: self.root.after(0, self.ocr.start_screenshot))
            
            messagebox.showinfo("成功", f"快捷键已更新为：{hotkey}")
        except Exception as e:
            messagebox.showerror("错误", f"设置快捷键失败：{str(e)}")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = OCRApp()
    app.run() 