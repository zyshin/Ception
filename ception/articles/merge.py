from diff_parser import DiffParser


def convert_diff_to_replace(diff):
    # diff: [(-1, 'This is a'), (1, u'Thawesa wega'), (0, ' example sentence whose target is to evaluate the performance of diff function modified by ZYShin.\n')]
    # return: [{'pos': (start, end), 'text': 'replace_text'}, {...}, ...]
    # assert -1 is left, 1 is right
    r = []
    start = 0
    i = 0
    while i < len(diff):
        change_type, text = diff[i]
        if change_type == -1:   # delete
            deleted = text
            added = ''
            if i < len(diff) - 1 and diff[i + 1][0] == 1:   # replace
                added = diff[i + 1][1]
                i += 1
        elif change_type == 1:  # add
            deleted = ''
            added = text
        if change_type == -1 or change_type == 1:
            r.append({
                'pos': (start, start + len(deleted)),
                'text': added,
            })
        if change_type == 0 or change_type == -1:
            start += len(text)
        i += 1
    return r

def merge_diff(user_diff, other_diff):
    # return: merged = [([d1, ...], [d2, ...]), ...]
    merged = []
    i = j = 0
    in_conflict = False
    while i < len(user_diff) or j < len(other_diff):
        if i >= len(user_diff) or (j < len(other_diff) and user_diff[i]['pos'][0] > other_diff[j]['pos'][1]):
            d2 = other_diff[j]
            if in_conflict:
                merged[-1][1].append(d2)
            else:
                merged.append(([d2], []))
            in_conflict = False
            j += 1
            continue
        if j >= len(other_diff) or (i < len(user_diff) and user_diff[i]['pos'][1] < other_diff[j]['pos'][0]):
            d1 = user_diff[i]
            if in_conflict:
                merged[-1][0].append(d1)
            else:
                merged.append(([d1], []))
            in_conflict = False    
            i += 1
            continue
        d1, d2 = user_diff[i], other_diff[j]
        if d1['pos'][1] < d2['pos'][1]:
            if in_conflict:
                merged[-1][0].append(d1)
            else:
                merged.append(([d1], []))
            i += 1
        else:
            if in_conflict:
                merged[-1][1].append(d2)
            else:
                merged.append(([], [d2]))
            j += 1
        if not in_conflict:
            in_conflict = True
    return merged

def apply_diff(origin_clean, diffs, _start=0, _end=None):
    if _end:
        _end = None if _end >= len(origin_clean) else _end - len(origin_clean)
    # assert origin_clean[diffs_start:diffs_end] in origin_clean[_start:_end]
    r = origin_clean
    for d in reversed(diffs):
        start, end = d['pos']
        delete = '<del>%s</del>' % r[start:end] if (end - start) else ''
        add = '<ins>%s</ins>' % d['text'] if d['text'] else ''
        r = r[:start] + delete + add + r[end:]
    return r[_start:_end]

def merge_edit(origin_clean, user_clean, other_clean):
    # data = {
    #     '0': [{'word': 'text', 'count': 1}, {'word': 'sentence', 'count': 2}],
    #     '1': [{'word': 'Shichao Yue', 'count': 3}, {'word': 'scyue', 'count': 4}],
    # }
    # html_str = 'This is a normal <div class="replace" data-pk="0">text</div> written by <div class="replace" data-pk="1">Shichao Yue</div>.'
    user_diff = convert_diff_to_replace(DiffParser.dmp.diff_wordMode(origin_clean, user_clean))
    other_diff = convert_diff_to_replace(DiffParser.dmp.diff_wordMode(origin_clean, other_clean))
    merged = merge_diff(user_diff, other_diff)

    html_str = origin_clean
    data = {}
    conflicted = 0
    for dd1, dd2 in reversed(merged):
        if dd2:   # conflicted
            conflicted = 1
            start = min([d['pos'][0] for d in dd1 + dd2])
            end = max([d['pos'][1] for d in dd1 + dd2])
            i = len(data)
            data[i] = [
                {'word': apply_diff(origin_clean, dd1, start, end), 'count': ''},
                {'word': apply_diff(origin_clean, dd2, start, end), 'count': ''},
            ]
            replace = '<div class="replace" data-pk="%d">%s</div>' % (i, data[i][0]['word'])
            html_str = html_str[:start] + replace + html_str[end:]
        else: # solved
            html_str = apply_diff(html_str, dd1)
    return html_str, data, conflicted


import unittest

class MergeTest(unittest.TestCase):

  def setUp(self):
    pass

  def test_convert_diff_to_replace(self):    
    diff = [(0, 'This is a '), (1, u'good '), (0, 'example sentence whose target is to evaluate the performance of '), (-1, 'diff function'), (1, u'difficultfunction'), (0, ' modified by ZYShin.\n')]
    converted = [
        {'pos': (10, 10), 'text': u'good '},
        {'pos': (74, 87), 'text': u'difficultfunction'},
    ]
    self.assertEquals(converted, convert_diff_to_replace(diff))

  def testMergeDiff(self):
    d1 = [
        {'text': u'a123ample', 'pos': (8, 17)},
        {'text': u'evaluawerte', 'pos': (46, 54)},
    ]
    d2 = [
        {'text': u'exasgabeqargple', 'pos': (10, 17)},
        {'text': u'targeawert', 'pos': (33, 39)},
    ]
    solved = [
        {'text': u'targeawert', 'pos': (33, 39)},
        {'text': u'evaluawerte', 'pos': (46, 54)},
    ]
    conflicts = [
        ([{'text': u'a123ample', 'pos': (8, 17)}], [{'text': u'exasgabeqargple', 'pos': (10, 17)}]),
    ]
    merged = [
        ([{'text': u'a123ample', 'pos': (8, 17)}], [{'text': u'exasgabeqargple', 'pos': (10, 17)}]),
        ([{'text': u'targeawert', 'pos': (33, 39)}], []),
        ([{'text': u'evaluawerte', 'pos': (46, 54)}], []),
    ]
    # self.assertEquals((solved, conflicts), merge_diff(d1, d2))
    self.assertEquals(merged, merge_diff(d1, d2))

    d1 = [
        {'text': ' the', 'pos': (0, 5)},
        {'text': 'ones', 'pos': (51, 60)},
    ]
    d2 = [
        {'text': 'them', 'pos': (25, 60)},
    ]
    solved = [
        {'text': ' the', 'pos': (0, 5)},
    ]
    conflicts = [
        ([{'text': 'ones', 'pos': (51, 60)}], [{'text': 'them', 'pos': (25, 60)}]),
    ]
    merged = [
        ([{'text': ' the', 'pos': (0, 5)}], []),
        ([{'text': 'ones', 'pos': (51, 60)}], [{'text': 'them', 'pos': (25, 60)}]),
    ]
    # self.assertEquals((solved, conflicts), merge_diff(d1, d2))
    self.assertEquals(merged, merge_diff(d1, d2))

  def testMergeEdit(self):
    origin_clean = 'Users can switch between monolingual and bilingual subtitles by clicking the button on the bottom right.'
    user_clean = 'Learners can switch between the monolingual subtitle and the bilingual ones by clicking the button on the bottom right.'
    other_clean = 'Users can switch between them by clicking the button on the bottom right.'
    origin_clean = 'This is a example sentence whose target is to evaluate the performance of diff function modified by ZYShin.'
    user_clean = 'This is a good example sentence whose target is to evaluate the performance of difficult function modified by ZYShin.'
    other_clean = 'These are example sentences whose target is to evaluate the performance of diff function modified by scyue.'
    user_diff = convert_diff_to_replace(DiffParser.dmp.diff_wordMode(origin_clean, user_clean))
    other_diff = convert_diff_to_replace(DiffParser.dmp.diff_wordMode(origin_clean, other_clean))
    # html_str, data = merge_edit(origin_clean, user_clean, other_clean)

    origin_clean = 'This is a example sentence whose target is to evaluate the performance of diff function modified by ZYShin.'
    user_clean = 'Thxaample sentence whose target is to evaluate the performance of diff function modified by ZYShin.'
    other_clean = 'T is a exbample sentence whose target is to evaluate the performance of diff function modified by ZYShin.'
    user_diff = convert_diff_to_replace(DiffParser.dmp.diff_wordMode(origin_clean, user_clean))
    other_diff = convert_diff_to_replace(DiffParser.dmp.diff_wordMode(origin_clean, other_clean))
    merged = [
        ([{'text': 'Thxaample', 'pos': (0, 17)}], [{'text': 'T', 'pos': (0, 4)}, {'text': 'exbample', 'pos': (10, 17)}]),
    ]
    self.assertEquals(merged, merge_diff(user_diff, other_diff))


if __name__ == "__main__":
  unittest.main()
