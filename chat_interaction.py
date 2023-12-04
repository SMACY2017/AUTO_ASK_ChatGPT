### chat_interaction.py

import pyautogui
import time
import pyperclip
import argparse
import random

class ChatInteraction:
    def __init__(self, screenshots_path):
        self.screenshots_path = screenshots_path

    def find_element(self, image_name, confidence=0.7):
        # 尝试找到屏幕上的元素
        if image_name=="response_end.png":
            confidence=0.9
        location = pyautogui.locateCenterOnScreen(f"{self.screenshots_path}/{image_name}", confidence=confidence)
        if location is not None:
            return location
        else:
            raise Exception(f"Element {image_name} not found on screen.")

    def move_to_element(self, image_name):
        # 获取元素位置
        position = self.find_element(image_name)
        
        # 随机化移动速度
        duration = random.uniform(0.2, 0.3)
        pyautogui.moveTo(position, duration=duration)

    def click_element(self, image_name):

        # 点击屏幕上的元素
        time.sleep(0.1)
        self.move_to_element(image_name)
        pyautogui.click()
        time.sleep(0.25)

    def start_new_chat(self):
        # 开启新的长对话
        
        self.click_element("new_chat.png")

    def paste_and_send_text(self, text):
        # 点击消息框，粘贴文本并发送
        self.click_element("message_box.png")
        # 使用ctrl+v粘贴文本
        time.sleep(0.8)  # 等待剪贴板内容更新
        pyperclip.copy(text)
        time.sleep(0.8)  # 等待复制完成
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.8)  # 等待剪贴板内容更新
        pyautogui.press('enter')

    def wait_for_response(self, timeout=30):
        start_time = time.time()
        time.sleep(5)  # 等待一秒后再次检查
        while True:
            # 检查是否已经过了超时时间
            if time.time() - start_time > timeout:
                raise TimeoutError("Response timeout reached")

            # 检测 response_end.png 是否出现
            try:
                self.find_element("response_end.png")
                return  # 如果找到了元素，结束等待
            except Exception:
                pass  # 如果没有找到元素，继续等待
            time.sleep(1)  # 等待一秒后再次检查


    def copy_response(self):
        response_text="没有复制到回应内容"
        # 复制回应内容
        self.click_element("response_end.png")
        time.sleep(1)  # 等待复制完成
        pyautogui.hotkey('ctrl', 'c')  # 复制到剪贴板
        time.sleep(1)  # 等待剪贴板内容更新
        response_text = pyperclip.paste() # 读取剪贴板内容
        return response_text

    def send_text_and_get_response(self, text):
        self.paste_and_send_text(text)
        self.wait_for_response()
        return self.copy_response()

    def continue_chat(self, text):
        response = self.send_text_and_get_response(text)
        return response

    def chat(self, text, new_conversation=True):
        try:
            if new_conversation:
                self.start_new_chat()
            response = self.continue_chat(text)
            return response
        except TimeoutError as e:
            # 特别处理超时异常
            raise e
        except Exception as e:
            print(f"Error: {e}")
            raise e

# 把send_text设置为可解析的命令行参数
if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--send_text", type=str, default="Hello, ChatGPT!")
    args = parser.parse_args()
    send_text = args.send_text

    # 使用示例
    screenshots_path = "./screenshots"  # 截图所在的文件夹路径
    chat_bot = ChatInteraction(screenshots_path)
    response = chat_bot.chat(send_text)  # 开始新对话
    print(response)

    # 继续当前对话
    follow_up_response = chat_bot.chat("Another question", new_conversation=False)
    print(follow_up_response)
