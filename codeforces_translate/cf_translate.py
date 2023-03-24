import re
from time import sleep
import requests
from bs4 import BeautifulSoup
from pygtrans import Translate
import html2text
import sys
import os

sleep_second = 0.2
client = Translate()


def html2md_cn(html):
    txt = str(html)
    txt = txt.replace("$$$", "$")
    txt = client.translate(txt, target='zh-CN').translatedText
    txt = html2text.html2text(txt)
    sleep(sleep_second)
    return txt


def sample_format(html):
    # 样例格式比较特殊，单独处理
    txt = ""
    txts = html.find_all(name="div")
    if txts:
        for i in txts:
            txt += i.string + "\n"
    else:
        txt = html.string
    txt = txt.strip()
    return txt


def get_html(url):
    cnt = 1
    while cnt <= 30:
        try:
            response = requests.get(url, timeout=10)
        except requests.exceptions.Timeout:
            cnt += 1
            continue
        if response.status_code == 200:
            return response.text
    print("请检查网络的联通性")


def get_problem(url):
    html = get_html(url)
    soup = BeautifulSoup(html, 'lxml')
    problems = soup.find_all(name="div", attrs={"class": "problem-statement"})
    problems_cn = ""
    for problem in problems:
        # 题目
        title = problem.find(name="div", attrs={"class": "title"}).contents[-1]
        problems_cn += "## " + title + "\n\n"

        # 时间限制
        problems_cn += "> 时间限制：" +\
                       problem.find(name="div", attrs={"class": "time-limit"}).contents[-1] +\
                       "  \n"

        # 空间限制
        problems_cn += "> 空间限制：" +\
                       problem.find(name="div", attrs={"class": "memory-limit"}).contents[-1] +\
                       "\n\n"

        # 题目描述
        description = problem.find_all("div", recursive=False)[1]
        description = html2md_cn(description)
        problems_cn += "### 题目描述\n\n" + description

        # 输入格式
        input = problem.find(name="div", attrs={
                             "class": "input-specification"})
        if input:
            input = html2md_cn(input)
            problems_cn += "### " + input

        # 输出格式
        output = problem.find_all("div", recursive=False)
        if len(output) >= 4:
            output = output[3]
            output = html2md_cn(output)
            problems_cn += "### " + output

        # 样例
        sample = problem.find(
            name="div", attrs={"class": "sample-test"})
        if sample:
            sample = sample.find_all(name="pre")
            cnt = 1
            for i in sample:
                txt = sample_format(i)
                if cnt % 2 == 1:
                    problems_cn += "### 输入 #"
                else:
                    problems_cn += "### 输出 #"
                problems_cn += str((cnt+1)//2)+"\n\n```txt\n"
                problems_cn += txt+"\n```\n\n"
                cnt += 1

        # 说明
        note = problem.find(name="div", attrs={
            "class": "note"})
        if note:
            note = note.contents[1:]
            note = [str(i) for i in note]
            note = " ".join(note)
            note = html2md_cn(note)
            problems_cn += "### 说明\n\n" + note

        # 完成该道题目的翻译
        print(f"Completed: {title}")

    return problems_cn


def main():
    id = sys.argv[1]
    url = "https://codeforces.com/"
    if int(id) >= 100000:
        url += "gym"
    else:
        url += "contest"
    url += "/"+id+"/"
    problem_id = ""
    if len(sys.argv) > 2 and sys.argv[2]:
        problem_id = sys.argv[2]
        url += f"problem/{problem_id}"
    else:
        url += "problems"
    print(url)
    problem_cn = get_problem(url)
    with open(f"./{id}{problem_id}.md", "w") as f:
        f.write(problem_cn)
        print(f"{os.getcwd()}/{id}{problem_id}.md")


if __name__ == "__main__":
    main()
