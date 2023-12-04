### csv_chat.py

import pandas as pd
import os
from chat_interaction import ChatInteraction
import logging
import json

# 设置日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def save_to_json(json_path, q_id, question, response):
    data_to_save = {q_id: {"question": question, "response": response}}
    try:
        if os.path.exists(json_path):
            with open(json_path, 'r+', encoding='utf-8') as file:
                existing_data = json.load(file)
                # 更新数据（如果 id 已存在，更新回答；否则添加新 id 和对应的问题-回答）
                existing_data.update(data_to_save)
                file.seek(0)
                file.truncate()
                json.dump(existing_data, file, ensure_ascii=False, indent=4)
        else:
            with open(json_path, 'w', encoding='utf-8') as file:
                # 创建一个新字典来保存数据
                json.dump(data_to_save, file, ensure_ascii=False, indent=4)
    except Exception as e:
        logging.error(f"保存到 JSON 文件时发生错误: {e}")



def process_csv(screenshots_path, csv_path, multi_conversation=False):
    chat_bot = ChatInteraction(screenshots_path)
    json_path = csv_path.replace('.csv', '.json')  # JSON 文件路径

    reply_count = 0
    max_replies = 40  # 设定的最大回复限制

    # 读取 CSV 文件
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path, encoding='utf-8')
        if 'answered' not in df.columns:
            df['answered'] = 'no'  # 添加状态列
    else:
        logging.error(f"CSV 文件 {csv_path} 不存在")
        return

    # 检查状态文件
    state_file = csv_path + '.state'
    start_row = 0
    if os.path.exists(state_file):
        with open(state_file, 'r') as f:
            start_row = int(f.read().strip())
            logging.info(f"继续之前的会话，从第 {start_row + 1} 行开始")

    for i, row in df.iterrows():
        if i < start_row or row['answered'] == 'yes':
            continue  # 跳过已处理的行
        if reply_count >= max_replies:
            logging.warning("已达到最大回复限制。请稍后再试。")
            break

        try:
            new_conversation = not multi_conversation or i == 0
            response = chat_bot.chat(row['question'], new_conversation=new_conversation)
            df.at[i, 'answered'] = 'yes'
            df.to_csv(csv_path, index=False, encoding='utf-8')

            logging.info(f"问题: {row['question']}")
            logging.info(f"回答: {response}")

            # 保存回答到 JSON
            save_to_json(json_path, row['id'], row['question'], response)

            # 更新状态文件
            with open(state_file, 'w') as f:
                f.write(str(i+1))

            reply_count += 1
        except TimeoutError as e:
            logging.error(f"获取回答时发生超时错误：{e}")
            break
        except Exception as e:
            logging.error(f"处理问题 '{row['question']}' 时发生错误: {e}")
            break

if __name__ == "__main__":
    screenshots_path = "./screenshots"
    csv_path = "./csv/example_questions_chinese.csv"  # 替换为实际的 CSV 文件路径
    process_csv(screenshots_path, csv_path, multi_conversation=False)
