import asyncio
import os
from openai import AsyncOpenAI

import pandas as pd

import tkinter as tk
from tkinter import filedialog
from tkinter.filedialog import askopenfilenames

import csv

from datetime import datetime
import time


root = tk.Tk()
root.withdraw()

OPENAI_API_KEY = "test"
client = AsyncOpenAI(api_key=OPENAI_API_KEY,  base_url="http://localhost:4000/v1")

def get_folder_or_file(fldr_nm, folder_or_not):
    root = tk.Tk()
    root.withdraw()

    if folder_or_not:
        folder_path = filedialog.askdirectory(title=f"Выберите папку с {fldr_nm}")
        root.destroy()
        return folder_path
    else:
        f_name = askopenfilenames(initialdir=r"C:",
                                  filetypes=((f"{fldr_nm} File", f"*.{fldr_nm}"), ("All Files", "*.*")),
                                  title=f"Выберите файл с {fldr_nm}"
                                  )
        root.destroy()
        return f_name


def read_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"Файл {file_path} не найден")
        return None
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return None


async def get_openai_response(prompt, row_content, ask_num):
    try:
        response = await client.chat.completions.create(
            model="Qwen/Qwen2.5-72B-Instruct",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": row_content}
            ],
            max_tokens=100,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Ошибка для {ask_num}: {e}"


async def process_file(ask_num, ask_to_model, semaphore, prompt, results_list):
    async with semaphore:
        prompt = read_from_file(prompt)

        if prompt:
            print(ask_num)
            print(ask_to_model)
            result = await get_openai_response(prompt, ask_to_model, ask_num)
            results_list.append({"ask_num": ask_num, "response": result})
            print(f"Завершено: {ask_num} -> {result}")

        else:
            results_list.append({"ask_num": ask_num, "response": "Не удалось прочитать текст"})
            print(f"Не удалось прочитать {ask_num}")


async def process_prompt_files(ask_num, ask_to_model, prompt_folder_path, results_list, max_concurrent=5):

    semaphore = asyncio.Semaphore(max_concurrent)

    tasks = []
    task = process_file(ask_num, ask_to_model, semaphore, prompt_folder_path, results_list)
    tasks.append(task)

    if tasks:
        await asyncio.gather(*tasks)
    else:
        print("Нет текста для обработки")
        return None

    df = pd.DataFrame(results_list, columns=["ask_num", "response"])
    return df


if __name__ == "__main__":
    file_type = 'csv'
    prompt_folder_path = get_folder_or_file("txt", 0)
    f_name = get_folder_or_file(file_type, 0)

    print(f"Выбран файл: {f_name}")
    print(f"Выбран промпт: {prompt_folder_path[0]}")

    start_time = time.time()
    for file_path in f_name:
        print(f"Обработка: \n {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                next(csv_reader)

                results_list = []

                for i, row in enumerate(csv_reader, start=1):
                    df = asyncio.run(process_prompt_files(i, ' '.join(row), prompt_folder_path[0], results_list, max_concurrent=5))

                if df is not None:
                    print("\nРезультаты в виде таблицы:")
                    print(df)

                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    base_name = os.path.basename(file_path).replace(f"'.'{file_type}", '')
                    output_file = f"output_{base_name.split('_')[1]}_{timestamp}"
                    df.to_csv(f"{output_file}.csv", index=False, encoding='utf-8')
                    df.to_excel(f"{output_file}.xlsx", index=False, engine='openpyxl')

                else:
                    print("Датафрейм не создан")

        except FileNotFoundError:
            print(f"Файл {file_path} не найден")
        except Exception as e:
            print(f"Произошла ошибка: {e}")




    end_time = time.time()
    execution_time = end_time - start_time
    print(f"\nВремя выполнения: {execution_time:.2f} секунд")
