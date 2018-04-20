"""
A lightweight wrapper over the stack overflow API.
So far allows querying for questions, and returns
all(or enough) answers associated with the question.

Usage:

    api = SOApi()
    qres = api.query_questions("Error using horzcat", pagesize=10)
    ares = api.query_answers([str(d["question_id"]) for d in res], pagesize=10)
"""
import requests
import json

from urllib.parse import urljoin


# Required properties of SOApi.
# If these don't exist inside of configfile,
# then we're definitely doing something wrong.
REQUIRED_FIELDS = ['version', 'site', 'base_url', 'question_fields']

class SOApi:
    def __init__(self, configfile="config.json"):
        try:
            with open(__file__configfile, "r") as f:
                self.__dict__ = json.load(f)
        except OSError as e:
            raise ValueError("Could not read {}. Encountered error {}."
                    .format(configfile, e))

        missing_fields = [field for field in REQUIRED_FIELDS if field not in self.__dict__ ]
        if missing_fields:
            raise ValueError("Missing some essential fields in config file: \n{}"
                    .format('\n'.join(missing_fields)))
        self.api_url = urljoin(self.base_url, self.version)
        self.question_fields = set(self.question_fields)
        self.answer_fields = set(self.answer_fields)

    def query_questions(self, q, sort="votes", filter="withbody", **kwargs):
        """
        Arguments:
        q : str, the actual query.
        sort : str, sort by "votes", or "activity", etc.
        filter : str, either "withbody", "default", "none", or a custom filter.
            We can't get the body of the questions unless we specify a filter.
        """
        payload = {'q' : q,
                'site' : self.site,
                'sort' : sort,
                'filter' : filter}
        payload.update(kwargs)
        r = requests.get(urljoin(self.api_url, "search/advanced"),
                params=payload)
        r.raise_for_status()
        j = r.json()['items']
        j = [ { k:v for k,v in question.items() if k in self.question_fields } for question in j ]
        return j

    def query_answers(self, qids, top_k=100, sort="votes", filter="withbody", **kwargs):
        """
        Arguments:
        qids : list[str], a list of question ids to query on.
        top_k : int, max number of queries for qids.
        sort : str, sort by "votes", or "activity", etc.
        filter : str, either "withbody", "default", "none", or a custom filter.
        """
        payload = { 'site' : self.site,
                'sort' : sort,
                'filter' : filter}
        payload.update(kwargs)
        ids = ";".join(qids[:top_k])
        r = requests.get(urljoin(self.api_url, "questions/{}/answers".format(ids)),
                params=payload)
        r.raise_for_status()
        j = r.json()['items']
        j = [ { k:v for k,v in answer.items() if k in self.answer_fields } for answer in j ]
        return j

if __name__ == "__main__":
    api = SOApi()
    qres = api.query_questions("Error using horzcat", pagesize=10)
    print(qres)
