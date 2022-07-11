#!/usr/bin/env python3

from jiraworklog.read_jira_worklogs import extract_worklog_fields, worklog_full_to_canon

def diff_worklogs_local(local, checkedin):
    diff_worklogs = make_diff_worklogs(
        create_augiss_local,
        create_augiss_jira
    )
    return diff_worklogs(local, checkedin)

def diff_worklogs_jira(remote, checkedin):
    diff_worklogs = make_diff_worklogs(
        create_augiss_jira,
        create_augiss_jira
    )
    # TODO: consider adding a step that updates the "extraneous" information in
    # a checked-in entry?
    return diff_worklogs(remote, checkedin)

def make_diff_worklogs(create_augiss_other, create_augiss_checkedin):
    def diff_worklogs(dictof_issue_1, dictof_issue_2):
        # TODO: assert that they keys are identical for the two?
        return {k: diff_issue_worklogs(dictof_issue_1[k], dictof_issue_2[k])
                for k
                in dictof_issue_1.keys()}
    # The efficiency of this algorithm could likely by improved. However, note
    # that we have to handle the possibility of duplicate worklog entries which
    # precludes us from doing certain things like using sets
    def diff_issue_worklogs(issue_other, issue_checkedin):
        augiss_other = create_augiss_other(issue_other)
        augiss_checkedin = create_augiss_checkedin(issue_checkedin)
        added = []
        for augwkl_other in augiss_other:
            found_match = False
            for i, augwkl_checkedin in enumerate(augiss_checkedin):
                if augwkl_checkedin['canon'] == augwkl_other['canon']:
                    found_match = True
                    augiss_checkedin.pop(i)
                    continue
            if not found_match:
                added.append(augwkl_other)
        return {
            'added': added,
            'removed': augiss_checkedin
        }
    return diff_worklogs

def create_augiss_jira(issue_local):
    augiss_jira = [create_augwkl_jira(wkl) for wkl in issue_local]
    return augiss_jira

def create_augwkl_jira(worklog_jira):
    full = extract_worklog_fields(worklog_jira)
    canon = worklog_full_to_canon(full)
    return {
        'canon': canon,
        'full': full,
        'jira': worklog_jira
    }

def create_augwkl_checkedin(worklog_checkedin):
    canon = worklog_full_to_canon(worklog_checkedin)
    return {
        'canon': canon,
        'full': worklog_checkedin
    }

def create_augwkl_local(worklog_local):
    return {
        'canon': worklog_local
    }

def create_augiss_local(issue_local):
    augiss_local = [{'canon': wkl}
                    for wkl
                    in issue_local]
    return augiss_local

def augm_wkls_jira(jira_issues):
    map_worklogs(create_augwkl_jira, jira_issues)

def augm_wkls_checkedin(checkedin_issues):
    map_worklogs(create_augwkl_checkedin, checkedin_issues)

def augm_wkls_local(local_issues):
    map_worklogs(create_augwkl_local, local_issues)

def map_worklogs(f, issues):
    {k: map(f, v) for k, v in issues}
