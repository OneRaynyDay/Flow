import runpy
import sys
import os
import subprocess
import so_api
import traceback
import re
from bs4 import BeautifulSoup
from html.parser import HTMLParser


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate

@static_vars(h=HTMLParser())
def parse_html(html, exclude_tags=None):
    print(parse_html.h.unescape(html))
    soup = BeautifulSoup(parse_html.h.unescape(html), "lxml")
    if not exclude_tags:
        exclude_tags = []
    for tag_name in exclude_tags:
        for tag in soup.findAll(tag_name):
            tag.extract()
    return soup.get_text()

def display_questions(qs, show_body=True, max_chars=100):
    dump = []
    for q in qs:
        title = parse_html(q["title"])
        dump.append("{} - \"{}\"".format(q["question_id"], title))
        if show_body:
            body = parse_html(q["body"], exclude_tags=["code"])
            dump.append("\t : {}".format(body[:max_chars]))
    for d in dump:
        print(d[:max_chars])

def display_answers(answers):
    dump = []
    h = HTMLParser() 
    for ans in answers:
        ans = parse_html(ans["body"])
        dump.append(ans)
    for d in dump:
        print(d)

module_name = os.path.splitext(sys.argv[1])[0]
try:
    runpy.run_module(module_name, {}, "__main__")
except Exception as e:
    print("caught exception:", e)
    err_traceback = traceback.format_exc()
    err = str(e)
# pyargs = sys.argv[1:]
# result = subprocess.run(["python"] + pyargs, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# if result.returncode:
#     stderr = result.stderr.decode("utf-8")
#     stdout = result.stdout.decode("utf-8")
#     eprint("Python interpreter error: \n{}".format(stderr))
#     print("Stdout hints: \n{}".format(stdout))

api = so_api.SOApi()
print("Asking: ", "Python, {}".format(err))
res = api.query_questions("Python, {}".format(err), tagged='python')

print("I have found these questions:")
display_questions(res, show_body=False)

print("Which one(s) are you interested in?")
qids = input().split(",")
res = api.query_answers(qids, pagesize=10)

print("I have found these answers:")
display_answers(res)
