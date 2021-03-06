#!/usr/bin/env python3

def check_remote_changes(altrep_head, altrep_remote):
    modifrep = create_modifrep(altrep_head, altrep_remote)
    modifgraphs = create_modifgraphs(modifrep)
    for graph in modifgraphs:
        pass


def create_modifrep(altrep_head, altrep_remote):

    # Create a dict with keys the worklog ID and values the "altrep"
    # representation of the worklogs
    def create_idrep(altrep):
        return {w['id']:k for (k, v) in altrep.items() for w in v}

    idrep_head = create_idrep(altrep_head)
    idrep_remote = create_idrep(altrep_remote)
    ids = set().union(idrep_head.keys(), idrep_remote.keys())

    # Create a dict with each element a list of sublists such that each sublist
    # is a lenth-1 list (in the case of `'added'` and `'removed'`) or length-2
    # list (in the case of `'updated'`) of worklog altrep keys
    #
    # Note that for the `not idrep_head[id] == idrep_remote[id]` case we can
    # assume that the worklog is in both head and remote
    modifrep = {'added': [], 'updated': [], 'removed': []}
    for id in ids:
        in_head = id in idrep_head.keys()
        in_remote = id in idrep_remote.keys()
        if in_head and not in_remote:
            modifrep['removed'].append([idrep_head[id]])
        elif not in_head and in_remote:
            modifrep['added'].append([idrep_head[id]])
        elif not idrep_head[id] == idrep_remote[id]:
            modifrep['updated'].append([idrep_head[id], idrep_remote[id]])

    return modifrep


def create_modifgraphs(modifrep):

    # Return True if any elements of `look_for` are in `look_in`, and return
    # False otherwise
    def check_in(look_for, look_in):
        for obj in look_for:
            if obj in look_in:
                return True
        return False

    modifgraphs = {}
    for modkey in ['added', 'updated', 'removed']:
        for altkeys in modifrep[modkey]:
            subgraph_keys = modifgraphs.keys()
            membersof = [k for k in subgraph_keys if check_in(altkeys, k)]
            if len(membersof) == 0:
                modifgraphs[tuple(altkeys)] = {
                    'added': [],
                    'updated': [],
                    'removed': []
                }
                modifgraphs[tuple(altkeys)][modkey].append(altkeys)
            elif len(altkeys) == 1:
                modifgraphs[membersof[0]][modkey].append(altkeys)
            elif len(membersof) == 2:
                subgraph_0 = modifgraphs[membersof[0]]
                subgraph_1 = modifgraphs[membersof[1]]
                newkey = (*membersof[0], *membersof[1])
                newval = {
                    'added': subgraph_0['added'] ++ subgraph_1['added'],
                    'updated': subgraph_0['updated'] ++ subgraph_1['updated'],
                    'removed': subgraph_0['removed'] ++ subgraph_1['removed']
                }
                newval[modkey].append(altkeys)
                del modifgraphs[membersof[0]]
                del modifgraphs[membersof[1]]
                modifgraphs[newkey] = newval
            elif altkeys[0] in membersof[0] and altkeys[1] in membersof[0]:
                modifgraphs[membersof[0]][modkey].append(altkeys)
            # Case:  either the 'from' or 'to' worklogs are already present
            # in a subgraph, but not both
            else:
                newkey_elem = (altkeys[0]
                                if altkeys[0] in membersof[0]
                                else altkeys[1])
                newkey = (*membersof[0], newkey_elem)
                newvalue = modifgraphs[membersof[0]][modkey].append(altkeys)
                del modifgraphs[membersof[0]]
                modifgraphs[newkey] = newvalue

    return modifgraphs
