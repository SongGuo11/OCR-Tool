import sys
# 移除版本检查，改为警告
if sys.version_info < (3, 11):  # 降低版本要求到 3.11
    print("警告: 建议使用 Python 3.11 或更高版本")
    # 不强制退出
    # sys.exit(1)

try:
    import keyboard
except ImportError:
    print("正在安装必要的依赖...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "keyboard"])
    import keyboard

import pyperclip
from PIL import ImageGrab, Image
import tkinter as tk
from tkinter import messagebox
import cv2
import numpy as np
from easyocr import Reader
import io
import traceback
import pytesseract
from PIL import ImageEnhance
from aip import AipOcr
import win32gui
import win32ui
import win32con
import win32api
from ctypes import windll
import ctypes

# 设置DPI感知
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    # Windows 8.1 及以下版本
    ctypes.windll.user32.SetProcessDPIAware()

class ScreenshotOCR:
    def __init__(self, app_id, api_key, secret_key):
        # 百度OCR配置
        self.APP_ID = app_id
        self.API_KEY = api_key
        self.SECRET_KEY = secret_key
        self.client = AipOcr(self.APP_ID, self.API_KEY, self.SECRET_KEY)
        
        # 初始化EasyOCR
        self.reader = Reader(['ch_sim','en'])
        
        # 设置Tesseract路径
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        self.root = None
        self.start_x = None
        self.start_y = None
        self.current_x = None
        self.current_y = None
        self.screenshot_window = None
        self.canvas = None

    def init_root(self, root):
        """初始化root窗口"""
        self.root = root

    def start_screenshot(self, event=None):
        """在主线程中调用此方法来创建截图窗口"""
        if not self.root:
            return
            
        # 确保在主线程中运行
        if self.screenshot_window:
            return
            
        # 获取虚拟屏幕的尺寸（包括所有显示器）
        left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
        top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
        width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
        height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
        
        # 创建全屏透明窗口
        self.screenshot_window = tk.Toplevel(self.root)
        self.screenshot_window.geometry(f"{width}x{height}+{left}+{top}")
        self.screenshot_window.attributes('-fullscreen', True, '-alpha', 0.3, '-topmost', True)
        
        # 创建画布
        self.canvas = tk.Canvas(self.screenshot_window, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 绑定事件
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        # 添加右键退出功能
        self.canvas.bind("<Button-3>", self.cleanup)  # 右键点击
        self.screenshot_window.bind("<Escape>", self.cleanup)  # ESC键

    def cleanup(self, event=None):
        """清理资源"""
        if self.screenshot_window:
            self.screenshot_window.destroy()
            self.screenshot_window = None
            self.canvas = None

    def capture_screen(self, x1, y1, x2, y2):
        """使用win32api进行截图"""
        width = x2 - x1
        height = y2 - y1
        
        if width <= 0 or height <= 0:
            return None
            
        try:
            # 创建DC和位图
            hwin = win32gui.GetDesktopWindow()
            hwindc = win32gui.GetWindowDC(hwin)
            srcdc = win32ui.CreateDCFromHandle(hwindc)
            memdc = srcdc.CreateCompatibleDC()
            bmp = win32ui.CreateBitmap()
            bmp.CreateCompatibleBitmap(srcdc, width, height)
            memdc.SelectObject(bmp)
            
            # 复制屏幕内容
            memdc.BitBlt((0, 0), (width, height), srcdc, (x1, y1), win32con.SRCCOPY)
            
            # 获取位图信息
            bmpinfo = bmp.GetInfo()
            bmpstr = bmp.GetBitmapBits(True)
            
            # 转换为PIL图像
            image = Image.frombuffer(
                'RGB',
                (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                bmpstr, 'raw', 'BGRX', 0, 1)
            
            # 清理资源
            win32gui.DeleteObject(bmp.GetHandle())
            memdc.DeleteDC()
            srcdc.DeleteDC()
            win32gui.ReleaseDC(hwin, hwindc)
            
            return image
            
        except Exception as e:
            print(f"截图失败: {str(e)}")
            return None

    def get_screen_coordinates(self, event):
        """获取真实的屏幕坐标"""
        # 获取鼠标相对于窗口的坐标
        window_x = event.x
        window_y = event.y
        
        # 获取窗口相对于屏幕的坐标
        screen_x = self.screenshot_window.winfo_rootx() + window_x
        screen_y = self.screenshot_window.winfo_rooty() + window_y
        
        return screen_x, screen_y

    def on_mouse_down(self, event):
        # 获取真实的屏幕坐标
        self.start_x, self.start_y = self.get_screen_coordinates(event)

    def on_mouse_move(self, event):
        # 获取真实的屏幕坐标
        self.current_x, self.current_y = self.get_screen_coordinates(event)
        
        # 清除之前的矩形
        self.canvas.delete("selection")
        
        # 转换回画布坐标绘制矩形
        canvas_start_x = self.start_x - self.screenshot_window.winfo_rootx()
        canvas_start_y = self.start_y - self.screenshot_window.winfo_rooty()
        canvas_current_x = self.current_x - self.screenshot_window.winfo_rootx()
        canvas_current_y = self.current_y - self.screenshot_window.winfo_rooty()
        
        # ���制矩形
        self.canvas.create_rectangle(
            canvas_start_x, canvas_start_y, 
            canvas_current_x, canvas_current_y,
            outline="red", tags="selection"
        )

    def preprocess_image(self, image):
        """图像预处理，提高识别率"""
        # 转换为OpenCV式
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # 计算合适的放大倍数（小图放大更多）
        height, width = opencv_image.shape[:2]
        if width * height < 10000:  # 小区域
            scale_percent = 400  # 放大4倍
        elif width * height < 40000:
            scale_percent = 300  # 放大3倍
        else:
            scale_percent = 200  # 放大2倍
            
        # 放大图像
        width = int(opencv_image.shape[1] * scale_percent / 100)
        height = int(opencv_image.shape[0] * scale_percent / 100)
        opencv_image = cv2.resize(opencv_image, (width, height), interpolation=cv2.INTER_CUBIC)
        
        # 增强对比度
        lab = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        l = clahe.apply(l)
        lab = cv2.merge((l,a,b))
        opencv_image = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        # 锐化处理
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        opencv_image = cv2.filter2D(opencv_image, -1, kernel)
        
        return opencv_image

    def enhance_image(self, image):
        """增强图像"""
        # 增强对比度
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        # 增强锐度
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.0)
        
        return image

    def tesseract_ocr(self, image):
        """使用Tesseract识别文字"""
        try:
            # 图像强
            enhanced_image = self.enhance_image(image)
            
            # 使用新的训练数据
            custom_config = r'--oem 3 --psm 6 -l chi_sim+eng'
            if image.size[0] * image.size[1] < 10000:  # 小区域
                # 放大图像
                width, height = image.size
                enhanced_image = enhanced_image.resize((width*4, height*4), Image.LANCZOS)
                custom_config += r' --dpi 300'  # 增加DPI
            
            text = pytesseract.image_to_string(enhanced_image, config=custom_config)
            return text.strip()
        except:
            return ""

    def easy_ocr(self, image):
        """使用EasyOCR识别图片文字"""
        try:
            # 图像预处理
            processed_image = self.preprocess_image(image)
            
            # 获取图像尺寸
            height, width = np.array(image).shape[:2]
            is_small_area = width * height < 10000
            
            # 针对小区域调整参数
            if is_small_area:
                result = self.reader.readtext(
                    processed_image,
                    detail=0,  # 只返回文本结果
                    paragraph=False,
                    contrast_ths=0.05,
                    adjust_contrast=0.7,
                    text_threshold=0.5,
                    width_ths=0.5,
                    height_ths=0.5,
                    low_text=0.3,
                    mag_ratio=2.0
                )
            else:
                result = self.reader.readtext(
                    processed_image,
                    detail=0,  # 只返回文本结果
                    paragraph=True,
                    contrast_ths=0.1,
                    adjust_contrast=0.5,
                    text_threshold=0.7,
                    width_ths=0.7,
                    height_ths=0.7
                )
            
            if result:
                return ' '.join(result)
            else:
                # 如果没有识别结果，尝试不进行预处理的原
                opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                # 对原图也进行放大
                scale = 4 if is_small_area else 2
                opencv_image = cv2.resize(opencv_image, None, fx=scale, fy=scale, 
                                       interpolation=cv2.INTER_CUBIC)
                result = self.reader.readtext(opencv_image, detail=0)
                if result:
                    return ' '.join(result)
            
        except Exception as e:
            print(f"EasyOCR识别失败：{str(e)}")
            print(traceback.format_exc())
        return ""

    def get_best_result(self, image):
        """获取最佳识别结果"""
        # 尝试两种识别方式
        easy_result = self.easy_ocr(image)
        tesseract_result = self.tesseract_ocr(image)
        
        # 选择更好的结果
        if not easy_result and not tesseract_result:
            return ""
        elif not easy_result:
            return tesseract_result
        elif not tesseract_result:
            return easy_result
        
        # 如果两种方法都有结果，选择更长的那个
        if len(easy_result) > len(tesseract_result):
            return easy_result
        return tesseract_result

    def baidu_accurate_ocr(self, image):
        """用百度精度OCR识别文字"""
        try:
            # 将图片转换为bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()

            # 调用高精度版
            options = {
                "detect_direction": "true",  # 检测文字方向
                "probability": "true",       # 返回识别结果置信度
                "detect_language": "true",   # 检测语言
                "paragraph": "true",         # 输出段落信
                "vertexes_location": "true", # 返回文字位置信息
                "recognize_granularity": "small" # 定位单字符位置
            }
            
            # 调用��用文字识别（高精度版）
            result = self.client.accurate(img_byte_arr, options)
            
            if 'words_result' in result:
                texts = []
                for words_result in result['words_result']:
                    if 'words' in words_result:
                        text = words_result['words'].strip()
                        if text:  # 只添加非空文本
                            texts.append(text)
                return ' '.join(texts)
            else:
                print("API返回结果中没有words_result字段：", result)
                if 'error_msg' in result:
                    print("错误信息：", result['error_msg'])
        except Exception as e:
            print(f"百度OCR识别失败：{str(e)}")
            print(traceback.format_exc())
        return ""

    def baidu_general_basic(self, image):
        """使用百度通用文字识别"""
        try:
            # 将图片转换为bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()

            # 调用通用文字识别
            result = self.client.basicGeneral(img_byte_arr)
            
            if 'words_result' in result:
                texts = []
                for words_result in result['words_result']:
                    if 'words' in words_result:
                        text = words_result['words'].strip()
                        if text:  # 只添加非空文本
                            texts.append(text)
                return ' '.join(texts)
            else:
                print("API返回结果中没有words_result字段：", result)
                if 'error_msg' in result:
                    print("错误信息：", result['error_msg'])
        except Exception as e:
            print(f"百度OCR识别失败：{str(e)}")
            print(traceback.format_exc())
        return ""

    def on_mouse_up(self, event):
        if self.start_x and self.start_y:
            try:
                # 获取真实的屏幕坐标
                x1 = min(self.start_x, self.current_x)
                y1 = min(self.start_y, self.current_y)
                x2 = max(self.start_x, self.current_x)
                y2 = max(self.start_y, self.current_y)
                
                # 打印截图区域信息
                print(f"截图区域: 左上角({x1}, {y1}), 右下角({x2}, {y2}), 宽度:{x2-x1}, 高度:{y2-y1}")
                
                # 先关闭截图窗口
                self.cleanup()
                
                # 使用win32api截图
                screenshot = self.capture_screen(x1, y1, x2, y2)
                
                if screenshot:
                    # 保存调试图片
                    debug_filename = "debug_screenshot.png"
                    screenshot.save(debug_filename)
                    print(f"已保存调试截图到: {debug_filename}")
                    
                    # OCR识别
                    text = self.baidu_general_basic(screenshot)
                    
                    if text:
                        print(f"识别结果: {text}")
                        pyperclip.copy(text)
                        messagebox.showinfo("成功", "文字已复制到剪贴板！")
                    else:
                        text = self.get_best_result(screenshot)
                        if text:
                            print(f"本地识别结果: {text}")
                            pyperclip.copy(text)
                            messagebox.showinfo("成功", "文字已复制到剪贴板！")
                        else:
                            messagebox.showwarning("警告", "未能识别出文字！")
                else:
                    messagebox.showerror("错误", "截图失败！")
                    
            except Exception as e:
                print(f"处理失败: {str(e)}")
                print(traceback.format_exc())
                messagebox.showerror("错误", f"处理失败: {str(e)}")
                self.cleanup()
        else:
            self.cleanup()

def main():
    app = ScreenshotOCR()
    # 注册快捷键 Ctrl+Alt+Z
    keyboard.add_hotkey('ctrl+alt+z', app.start_screenshot)
    print("程序已启动！按Ctrl+Alt+Z开始截图，按Ctrl+C退出程序。")
    
    try:
        app.root.mainloop()
    except KeyboardInterrupt:
        print("\n程序已退出！")
        sys.exit(0)

if __name__ == "__main__":
    main() 