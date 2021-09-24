#!/usr/bin/env python3

import json
# from jira import JIRA

def fetch_worklogs(jira, issue_nms, path):
    if not isinstance(issue_nms, list):
        raise Exception("'issue_nms' must be a list")
    if not all([isinstance(x, str) for x in issue_nms]):
        raise Exception("all elements of 'issue_nms' must be a string")
    with open(path, "w") as file:
        worklogs_dict = fetch_worklogs_remotedata(jira, issue_nms)
        json.dump(worklogs_dict, file, indent=4)
        file.write("\n")
    return worklogs_dict

# Why does `jira.worklogs` require a network call? It seems like the issue
# already contains all of the data
def fetch_worklogs_remotedata(jira, issue_nms):
    issues = [jira.issue(nm) for nm in issue_nms]
    # IDs are immutable but keys can change, for example when an issue moves to
    # another project. See
    # https://community.atlassian.com/t5/Agile-questions/Unique-Issue-ID-where-do-we-stand/qaq-p/586280?tempId=eyJvaWRjX2NvbnNlbnRfbGFuZ3VhZ2VfdmVyc2lvbiI6IjIuMCIsIm9pZGNfY29uc2VudF9ncmFudGVkX2F0IjoxNjMyMTU0MzIzNDMxfQ%3D%3D
    worklogs = {(x.key + "@" + x.id): jira.worklogs(x) for x in issues}
    return {k: [extract_worklog_fields(x) for x in v] for (k, v) in worklogs.items()}

def extract_worklog_fields(worklog):
    raw = worklog.raw
    return {
        'author': raw['author']['displayName'],
        'comment': raw['comment'],
        'created': raw['created'],
        'id': raw['id'],
        'issueId': raw['issueId'],
        'timeSpent': raw['timeSpent'],
        'timeSpentSeconds': raw['timeSpentSeconds'],
        'updateAuthor': raw['updateAuthor']['displayName'],
        'updated': raw['updated'],
    }
