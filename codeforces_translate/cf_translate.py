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


# 将获取到的html转为中文
def html2str(html):
    string = []
    for i in html:
        i = str(i).replace("\n", "") \
                  .replace("$$$$$$", " $$$$$$ ")
        i = re.sub(r'(?<!\$)\${3}(?!\$)', ' $$$ ', i)
        i = re.sub(r"<.*?>", "", i)
        string.append(i)
    string = [i.translatedText
              for i in client.translate(string, target='zh-CN')]
    for i in range(len(string)):
        string[i] = re.sub(r'(?<!\$)\$(?!\$)', '', string[i])
        string[i] = re.sub(r'(?<!\$)\${2}(?!\$)', '$$$', string[i])

        string[i] = string[i].replace("$$$", "$")\
                             .replace("$$$", "$$")\
                             .replace("&quot;", '"')\
                             .replace("&#39;", "'")\
                             .replace("&lt;", "\\lt")
        string[i] += "\n\n"
    string = "".join(string)
    sleep(sleep_second)
    return string

def get_html(url):
    cnt = 1 
    while cnt <= 30:
        try:
            response = requests.get(url, timeout = 10)
        except requests.exceptions.Timeout:
            cnt += 1
            continue
        if response.status_code == 200:
            return response.text
    print("请检查网络的联通性")

# 获取url下的中文markdown
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
        description = problem.find_all("div", recursive=False)[1].contents
        description = html2str(description)
        problems_cn += "### 题目描述\n\n" + description

        # 输入格式
        input_format = problem.find(
            name="div", attrs={"class": "input-specification"})
        if input_format != None:
            input_format = input_format.contents[1:]
            input_format = html2str(input_format)
            problems_cn += "### 输入格式\n\n" + input_format

        # 输出格式
        output_format = problem.find_all("div", recursive=False)
        if len(output_format) >= 4:
            output_format = output_format[3]
            output_format = html2str(output_format.contents[1:])
            problems_cn += "### 输出格式\n\n" + output_format

        # 样例
        sample = problem.find(
            name="div", attrs={"class": "sample-test"})
        if sample != None:
            sample = sample.find_all(name="pre")
            cnt = 1
            for i in sample:
                i = html2text.html2text(str(i))
                i = i.split("\n")
                temp = ""
                for j in i:
                    j = j.split(" ")
                    j = " ".join([k for k in j if k != ""])
                    if j != "":
                        temp += "\n"+j
                if cnt % 2 == 1:
                    problems_cn += "### 输入 #"
                else:
                    problems_cn += "### 输出 #"
                problems_cn += str((cnt+1)//2)+"\n\n```txt"
                problems_cn += temp+"\n```\n\n"
                cnt += 1

        # 说明
        note = problem.find(name="div", attrs={
            "class": "note"})
        if note != None :
            note = note.contents[1:]
            note = html2str(note)
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
