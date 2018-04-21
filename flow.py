import runpy
import sys
import os
import subprocess
import so_api
import traceback
import re
import tempfile
import webbrowser
import pprint

from collections import defaultdict
from bs4 import BeautifulSoup
from html.parser import HTMLParser

pp = pprint.PrettyPrinter(indent=4)

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
    soup = BeautifulSoup(parse_html.h.unescape(html), "lxml")
    if not exclude_tags:
        exclude_tags = []
    for tag_name in exclude_tags:
        for tag in soup.findAll(tag_name):
            tag.extract()
    return soup.get_text()

def display_questions(qs, show_body=True, max_chars=100, stdout=True):
    dump = []
    for i,q in enumerate(qs):
        title = parse_html(q["title"])
        dump.append("{} - \"{}\"".format(i, title))
        if show_body:
            body = parse_html(q["body"], exclude_tags=["code"])
            dump.append("\t : {}".format(body[:max_chars]))
    if not stdout:
        return dump
    for d in dump:
        print(d[:max_chars])

def display_answers(answers, stdout=True):
    qa_multimap = defaultdict(list)
    for ans in answers:
        qa_multimap[ans["question_id"]].append(ans)
    qa_multimap = dict(qa_multimap)
    if not stdout:
        return qa_multimap
    for d in qa_multimap:
        for a in qa_multimap[d]:
            print("{} : ".format(d, a))

@static_vars(editor=os.environ.get('EDITOR','vim'))
def open_editor(text):
    with tempfile.NamedTemporaryFile(suffix=".tmp") as tf:
      tf.write(text.encode())
      tf.flush()
      subprocess.run([open_editor.editor, tf.name])

def open_webbrowser(text):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tf:
      tf.write(text.encode())
      tf.flush()
      webbrowser.open('file://' + tf.name)

module_name = os.path.splitext(sys.argv[1])[0]
try:
    runpy.run_module(module_name, {}, "__main__")
except Exception as e:
    print("caught exception:", e)
    err_traceback = traceback.format_exc()
    err = str(e).split()
    err = " ".join(["".join([i for i in e if i.isalpha()]) for e in err])
    print("Fuck! You just ran into an error. Want to stack overflow it? [y/n]:")
    res = input()
    while res not in {"y", "n"}:
        res = input()
    if res == "n":
        sys.exit(1)

# pyargs = sys.argv[1:]
# result = subprocess.run(["python"] + pyargs, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# if result.returncode:
#     stderr = result.stderr.decode("utf-8")
#     stdout = result.stdout.decode("utf-8")
#     eprint("Python interpreter error: \n{}".format(stderr))
#     print("Stdout hints: \n{}".format(stdout))

api = so_api.SOApi()
print("Asking: ", "python {}".format(err))
qres = api.query_questions("Python, {}".format(err), tagged='python')

print("I have found these questions:")
display_questions(qres, show_body=False)

print("Which one(s) are you interested in?")
qids = input().split(",")

idxmap = {qres[int(qid)]["question_id"] : int(qid) for qid in qids}
qids = [str(qres[int(qid)]["question_id"]) for qid in qids]
ares = api.query_answers(qids, pagesize=10)

print("I have found these answers:")
ares = display_answers(ares, stdout=False)

qentries = []
for qid in ares:
    question = qres[idxmap[qid]]
    qstr = "<header>Title : {}</header>\n <header>Description : {} \n".format(question["title"], question["body"])
    astrs = ""
    for ans in ares[qid]:
        pp.pprint(ans)
        astrs += "<header>Answer from {}:</header>\n{}\n".format(ans["owner"]["display_name"], ans["body"])
    qentries.append(qstr+astrs)

open_webbrowser("\n-------\n".join(qentries))
