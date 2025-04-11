import asyncio
import os
from openai import AsyncOpenAI

import pandas as pd

import tkinter as tk
from tkinter import filedialog
from tkinter.filedialog import askopenfilenames

root = tk.Tk()
root.withdraw()

OPENAI_API_KEY = "test"
client = AsyncOpenAI(api_key=OPENAI_API_KEY,  base_url="http://localhost:4000/v1")

def get_folder_name(fldr_nm, folder_or_not):
    root = tk.Tk()
    root.withdraw()

    if folder_or_not:
        folder_path = filedialog.askdirectory(title=f"Выберите папку с {fldr_nm}")
        root.destroy()
        return folder_path
    else:
        f_name = askopenfilenames(initialdir=r"C:",
                                  filetypes=(("txt File", "*.txt"), ("All Files", "*.*")),
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


async def get_openai_response(prompt, file_content, filename):
    try:
        response = await client.chat.completions.create(
            model="Qwen/Qwen2.5-72B-Instruct",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": file_content}
            ],
            max_tokens=100,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Ошибка для {filename}: {e}"


async def process_file(file_path, semaphore, prompt, results_list):
    async with semaphore:
        filename = os.path.basename(file_path)
        prompt = read_from_file(prompt)
        file_content = read_from_file(file_path)

        if prompt:
            result = await get_openai_response(prompt, file_content, filename)
            filename_without_txt = os.path.splitext(filename)[0]
            results_list.append({"filename": filename_without_txt, "response": result})
            print(f"Завершено: {filename_without_txt} -> {result}")

        else:
            results_list.append({"filename": filename, "response": "Не удалось прочитать файл"})
            print(f"Не удалось прочитать файл из {filename}")


async def process_prompt_files(folder_path, prompt_folder_path, max_concurrent=5):

    if not os.path.exists(folder_path):
        print(f"Папка {folder_path} не найдена")
        return

    semaphore = asyncio.Semaphore(max_concurrent)
    results_list = []

    tasks = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            task = process_file(file_path, semaphore, prompt_folder_path, results_list)
            tasks.append(task)

    if tasks:
        await asyncio.gather(*tasks)
    else:
        print("Нет текстовых файлов для обработки")
        return None

    df = pd.DataFrame(results_list, columns=["filename", "response"])
    return df


if __name__ == "__main__":
    prompt_folder_path = get_folder_name("промпт", 0)
    folder_path = get_folder_name("текст", 1)

    folder_name = os.path.basename(folder_path)

    print(f"Выбрана папка: {folder_name}")
    print(f"Выбран промпт: {prompt_folder_path[0]}")

    df = asyncio.run(process_prompt_files(folder_path, prompt_folder_path[0], max_concurrent=5))

    if df is not None:
        print("\nРезультаты в виде таблицы:")
        print(df)

        df.to_csv("out.csv", index=False, encoding='utf-8')
        df.to_excel("out.xlsx", index=False, engine='openpyxl')
    else:
        print("Датафрейм не создан")
