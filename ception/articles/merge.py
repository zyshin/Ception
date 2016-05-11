from diff_parser import DiffParser

def diff_wordsToChars(text1, lineArray):
  lineHash = dict(zip(lineArray, xrange(len(lineArray))))

  def diff_wordsToCharsMunge(text):
    chars = []
    # Walk the text, pulling out a substring for each line.
    text = text.replace(',', ' , ').replace('.', ' . ').replace(';', ' ; ').replace(':', ' : ').replace('?', ' ? ').replace('!', ' ! ')
    for line in text.split():
      if line in lineHash:
        chars.append(unichr(lineHash[line]))
      else:
        lineArray.append(line)
        lineHash[line] = len(lineArray) - 1
        chars.append(unichr(len(lineArray) - 1))
    return "".join(chars)

  return diff_wordsToCharsMunge(text1)

def diff_charsToWords(s, wordArray):
  text = ' '.join([wordArray[ord(char)] for char in s])
  text = text.replace(' ,', ',').replace(' .', '.').replace(' ;', ';').replace(' :', ':').replace(' ?', '?').replace(' !', '!')
  if text:
    # start_space = '' if text[0] in ',.;:?!' else ' '
    start_space = ' '
    # TODO: handle punct spaces
    text = start_space + text + ' '
  return text

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
    # remove duplicated conflicts
    for dd1, dd2 in merged:
        if dd2 == dd1:
            dd2[:] = []
    return merged

import sys
from collections import deque

def merge_diff2(diffs):
    # return: merged = [{'user_id_1': [d1, ...], 'user_id_2': [d2, ...]}, ...]

    def pop_min(diffs):
        poss = [diff[0]['pos'][0] if len(diff) else sys.maxint for diff in diffs]
        min_pos = min(poss)
        if min_pos == sys.maxint:    # diffs are all empty
            return -1, None
        index = poss.index(min_pos)
        d = diffs[index].popleft()
        return index + 1, d

    diffs = [deque(diff) for diff in diffs]
    merged = []
    merged_end_pos = -1
    while True:
        index, d = pop_min(diffs)
        if not d:
            break
        if d['pos'][0] <= merged_end_pos:    # conflicted
            merged[-1][index] = merged[-1].get(index, [])
            merged[-1][index].append(d)
        else:   # no conflicts
            merged.append({index: [d]})
        merged_end_pos = max(merged_end_pos, d['pos'][1])
    return merged

# def apply_diff(origin_clean, diffs, _start=0, _end=None):
#     if _end:
#         _end = None if _end >= len(origin_clean) else _end - len(origin_clean)
#     # assert origin_clean[diffs_start:diffs_end] in origin_clean[_start:_end]
#     r = origin_clean
#     for d in reversed(diffs):
#         start, end = d['pos']
#         delete = '<del>%s</del>' % r[start:end] if (end - start) else ''
#         add = '<ins>%s</ins>' % d['text'] if d['text'] else ''
#         r = r[:start] + delete + add + r[end:]
#     r = r[_start:_end]
#     r = r.replace('<del> ', '<del>&nbsp;').replace(' </del>', '&nbsp;</del>').replace('<ins> ', '<ins>&nbsp;').replace(' </ins>', '&nbsp;</ins>')
#     if r.startswith(' '):
#         r = '&nbsp;' + r[1:]
#     if r.endswith(' '):
#         r = r[:-1] + '&nbsp;'
#     return r

def apply_diff2(wordArray, origin_clean, diffs, _start=0, _end=None):
    if _end:
        _end = None if _end >= len(origin_clean) else _end - len(origin_clean)
    __end = len(origin_clean) if not _end else _end
    # assert origin_clean[diffs_start:diffs_end] in origin_clean[_start:_end]
    # assert _end < 0 or _end == None
    r = origin_clean
    diffs = diffs + [{'pos': (__end, __end), 'text': ''}]
    for i in reversed(xrange(len(diffs))):
        d = diffs[i]
        start, end = d['pos']
        delete = '<del>%s</del>' % diff_charsToWords(r[start:end], wordArray) if (end - start) else ''
        add = '<ins>%s</ins>' % diff_charsToWords(d['text'], wordArray) if d['text'] else ''
        r = r[:start] + delete + add + r[end:]
        pre_end = diffs[i - 1]['pos'][1] if i > 0 else 0
        pre_end = max(pre_end, _start)
        r = r[:pre_end] + diff_charsToWords(r[pre_end:start], wordArray) + r[start:]
    r = r[_start:_end]
    # r = r.replace('<del> ', '<del>&nbsp;').replace(' </del>', '&nbsp;</del>').replace('<ins> ', '<ins>&nbsp;').replace(' </ins>', '&nbsp;</ins>')
    # if r.startswith(' '):
    #     r = '&nbsp;' + r[1:]
    # if r.endswith(' '):
    #     r = r[:-1] + '&nbsp;'
    return r

def merge_edit(origin_clean, user_clean, other_clean):
    # data = {
    #     '0': [{'key': 'to replace', 'word': 'text', 'count': 1}, {'key': 'to replace', 'word': 'sentence', 'count': 2}],
    #     '1': [{'key': 'to replace', 'word': 'Shichao Yue', 'count': 3}, {'key': 'to replace', 'word': 'scyue', 'count': 4}],
    # }
    # html_str = 'This is a normal <div class="replace" data-pk="0">text</div> written by <div class="replace" data-pk="1">Shichao Yue</div>.'
    wordArray = ['']
    origin_clean = diff_wordsToChars(origin_clean, wordArray)
    user_clean = diff_wordsToChars(user_clean, wordArray)
    other_clean = diff_wordsToChars(other_clean, wordArray)
    user_diff = convert_diff_to_replace(DiffParser.dmp.diff_main(origin_clean, user_clean))
    other_diff = convert_diff_to_replace(DiffParser.dmp.diff_main(origin_clean, other_clean))
    merged = merge_diff(user_diff, other_diff)

    html_str = origin_clean
    data = {}
    conflicted = 0
    merged = merged + [([{'pos': (len(origin_clean), len(origin_clean)), 'text': ''}], [])]
    for i in reversed(xrange(len(merged))):
        dd1, dd2 = merged[i]
        start = min([d['pos'][0] for d in dd1 + dd2])
        end = max([d['pos'][1] for d in dd1 + dd2])
        if dd2:   # conflicted
            conflicted = 1
            j = len(data)
            data[j] = [
                {'key': apply_diff2(wordArray, origin_clean, dd1, start, end), 'count': '&nbsp;mine&nbsp;'},
                {'key': apply_diff2(wordArray, origin_clean, dd2, start, end), 'count': 'others'},
            ]
            for o in data[j]:
                if o['key'].rfind('<del>') == 0 and o['key'].find('</del>') == (len(o['key']) - len('</del>')):
                    o['word'] = '<i>(deleted)</i>'
                else:
                    o['word'] = o['key']
            replace = '<div class="replace" data-pk="%d">%s</div>' % (j, data[j][0]['key'])
        else: # solved
            replace = apply_diff2(wordArray, origin_clean, dd1, start, end)
        html_str = html_str[:start] + replace + html_str[end:]

        pre_end = max([d['pos'][1] for d in merged[i - 1][0] + merged[i - 1][1]]) if i > 0 else 0
        html_str = html_str[:pre_end] + diff_charsToWords(html_str[pre_end:start], wordArray) + html_str[start:]
    return html_str, data, conflicted

from itertools import groupby

def summary_edit(sentence_list):
    # data = [
    #     [{'key': 'to replace', 'authors': [1, 2]}, {'key': 'to replace', 'authors': [3, 4]}],
    #     [{'key': 'to replace', 'authors': [1]}, {'key': 'to replace', 'authors': [2]}],
    # ]
    # ('word': key if key is only del else 'deleted', 'count': len(authors))
    # html_str = 'This is a normal <div class="replace" data-pk="0">text</div> written by <div class="replace" data-pk="1">Shichao Yue</div>.'
    # assert len(sentence_list) > 1
    wordArray = ['']
    sentence_list = [diff_wordsToChars(s, wordArray) for s in sentence_list]
    origin_clean = sentence_list[0]
    diffs = [convert_diff_to_replace(DiffParser.dmp.diff_main(origin_clean, s)) for s in sentence_list[1:]]
    merged = merge_diff2(diffs)

    html_str = origin_clean
    data = []
    conflicted = 0
    merged = merged + [{0: [{'pos': (len(origin_clean), len(origin_clean)), 'text': ''}]}]
    for i in reversed(xrange(len(merged))):
        diff = merged[i]
        start = min([dd[0]['pos'][0] for uid, dd in diff.iteritems()])
        end = max([dd[-1]['pos'][1] for uid, dd in diff.iteritems()])
        l = []
        for dd, diffs in groupby(sorted(diff.iteritems(), key=lambda o: o[1]), key=lambda o: o[1]):
            o = {
                'key': apply_diff2(wordArray, origin_clean, dd, start, end),
                'authors': sorted([uid for uid, dd in diffs]),
            }
            o['word'] = '<i>(deleted)</i>' if o['key'].rfind('<del>') == 0 and o['key'].find('</del>') == (len(o['key']) - len('</del>')) else o['key']
            o['count'] = len(o['authors'])
            l.append(o)
        l.sort(key=lambda o: (-o['count'], o['authors'][0]))

        if len(l) > 1:
            conflicted = 1
            replace = '<div class="replace" data-pk="%d">%s</div>' % (len(data), l[0]['key'])
            data.append(l)
        else:
            replace = l[0]['key']
        html_str = html_str[:start] + replace + html_str[end:]

        pre_end = max([dd[-1]['pos'][1] for uid, dd in merged[i - 1].iteritems()]) if i > 0 else 0
        html_str = html_str[:pre_end] + diff_charsToWords(html_str[pre_end:start], wordArray) + html_str[start:]
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
    
    origin_clean = 'This is a example sentence whose target is to evaluate the performance of diff function modified by ZYShin.'
    user_clean = 'Thxaample sentence whose target is to evaluate the performance of diff function modified by ZYShin.'
    other_clean = 'T is a exbample sentence whose target is to evaluate the performance of diff function modified by ZYShin.'
    user_diff = convert_diff_to_replace(DiffParser.dmp.diff_wordMode(origin_clean, user_clean))
    other_diff = convert_diff_to_replace(DiffParser.dmp.diff_wordMode(origin_clean, other_clean))
    merged = [
        ([{'text': 'Thxaample', 'pos': (0, 17)}], [{'text': 'T', 'pos': (0, 4)}, {'text': 'exbample', 'pos': (10, 17)}]),
    ]
    self.assertEquals(merged, merge_diff(user_diff, other_diff))

    origin_clean = 'In this section, we explore the feasibility of using subtitles for building video augmented dictionary'
    user_clean = 'In this section, we explore the feasibility of compiling video augmented dictionary for learners from subtitles'
    other_clean = 'In this section, we explore the feasibility of  building video augmented dictionary with subtitle'
    user_diff = convert_diff_to_replace(DiffParser.dmp.diff_wordMode(origin_clean, user_clean))
    other_diff = convert_diff_to_replace(DiffParser.dmp.diff_wordMode(origin_clean, other_clean))
    merged = [
        ([{'text': 'compiling', 'pos': (47, 75)}], [{'text': '', 'pos': (47, 66)}]),
        ([{'text': 'for learners from subtitles', 'pos': (103, 103)}], [{'text': 'with subtitle', 'pos': (103, 103)}]),
    ]
    self.assertEquals(merged, merge_diff(user_diff, other_diff))

  def testMergeDiff2(self):
    d1 = [
        {'text': u'a123ample', 'pos': (8, 17)},
        {'text': u'evaluawerte', 'pos': (46, 54)},
    ]
    d2 = [
        {'text': u'exasgabeqargple', 'pos': (10, 17)},
        {'text': u'targeawert', 'pos': (33, 39)},
    ]
    merged = [
        {1: [{'text': u'a123ample', 'pos': (8, 17)}], 2: [{'text': u'exasgabeqargple', 'pos': (10, 17)}]},
        {2: [{'text': u'targeawert', 'pos': (33, 39)}]},
        {1: [{'text': u'evaluawerte', 'pos': (46, 54)}]},
    ]
    # self.assertEquals((solved, conflicts), merge_diff(d1, d2))
    self.assertEquals(merged, merge_diff2([d1, d2]))

    d1 = [
        {'text': ' the', 'pos': (0, 5)},
        {'text': 'ones', 'pos': (51, 60)},
    ]
    d2 = [
        {'text': 'them', 'pos': (25, 60)},
    ]
    merged = [
        {1: [{'text': ' the', 'pos': (0, 5)}]},
        {1: [{'text': 'ones', 'pos': (51, 60)}], 2: [{'text': 'them', 'pos': (25, 60)}]},
    ]
    # self.assertEquals((solved, conflicts), merge_diff(d1, d2))
    self.assertEquals(merged, merge_diff2([d1, d2]))
    
    origin_clean = 'This is a example sentence whose target is to evaluate the performance of diff function modified by ZYShin.'
    user_clean = 'Thxaample sentence whose target is to evaluate the performance of diff function modified by ZYShin.'
    other_clean = 'T is a exbample sentence whose target is to evaluate the performance of diff function modified by ZYShin.'
    user_diff = convert_diff_to_replace(DiffParser.dmp.diff_wordMode(origin_clean, user_clean))
    other_diff = convert_diff_to_replace(DiffParser.dmp.diff_wordMode(origin_clean, other_clean))
    merged = [
        {1: [{'text': 'Thxaample', 'pos': (0, 17)}], 2: [{'text': 'T', 'pos': (0, 4)}, {'text': 'exbample', 'pos': (10, 17)}]},
    ]
    self.assertEquals(merged, merge_diff2([user_diff, other_diff]))

    origin_clean = 'In this section, we explore the feasibility of using subtitles for building video augmented dictionary'
    user_clean = 'In this section, we explore the feasibility of compiling video augmented dictionary for learners from subtitles'
    other_clean = 'In this section, we explore the feasibility of  building video augmented dictionary with subtitle'
    user_diff = convert_diff_to_replace(DiffParser.dmp.diff_wordMode(origin_clean, user_clean))
    other_diff = convert_diff_to_replace(DiffParser.dmp.diff_wordMode(origin_clean, other_clean))
    merged = [
        {1: [{'text': 'compiling', 'pos': (47, 75)}], 2: [{'text': '', 'pos': (47, 66)}]},
        {1: [{'text': 'for learners from subtitles', 'pos': (103, 103)}], 2: [{'text': 'with subtitle', 'pos': (103, 103)}]},
    ]
    self.assertEquals(merged, merge_diff2([user_diff, other_diff]))

    origin_clean = 'In this section, we explore the feasibility of using subtitles for building video augmented dictionary'
    user_clean = 'In this section, we explore the feasibility of video augmented dictionary for learners from subtitles'
    other_clean = 'In this section, we explore the feasibility of  building video augmented dictionary with subtitle'
    user_diff = convert_diff_to_replace(DiffParser.dmp.diff_wordMode(origin_clean, user_clean))
    other_diff = convert_diff_to_replace(DiffParser.dmp.diff_wordMode(origin_clean, other_clean))
    # merged = [
    #     ([{'text': '', 'pos': (47, 75)}], [{'text': '', 'pos': (47, 66)}]),
    #     ([{'text': ' for learners from subtitles', 'pos': (102, 102)}], [{'text': ' with subtitle', 'pos': (102, 102)}])
    # ]
    # self.assertEquals(merged, merge_diff(user_diff, other_diff))

  def testMerge(self):
    # origin_clean = 'Users can switch between monolingual and bilingual subtitles by clicking the button on the bottom right.'
    # user_clean = 'Learners can switch between the monolingual subtitle and the bilingual ones by clicking the button on the bottom right.'
    # other_clean = 'Users can switch between them by clicking the button on the bottom right.'
    origin_clean = 'This is a example sentence whose target is to evaluate the performance of diff function modified by ZYShin.'
    user_clean = 'This is a good example sentence whose target is to evaluate the performance of difficult function modified by ZYShin.'
    other_clean = 'These are example sentences whose target is to evaluate the performance of diff function modified by scyue.'
    html_str, data, conflicted = merge_edit(origin_clean, user_clean, other_clean)
    html_str2, data2, conflicted2 = summary_edit([origin_clean, user_clean, other_clean])
    self.assertEquals(html_str, html_str2)
    data = [v for k, v in sorted(data.iteritems(), key=lambda o: o[0])]
    for oo in data:
        for o in oo:
            o['count'] = 1
    for oo in data2:
        for o in oo:
            del o['authors']
    self.assertEquals(data, data2)
    self.assertEquals(conflicted, conflicted2)

    origin_clean = 'In this section, we explore the feasibility of using subtitles for building video augmented dictionary'
    user_clean = 'In this section, we explore the feasibility of video augmented dictionary for learners from subtitles'
    other_clean = 'In this section, we explore the feasibility of  building video augmented dictionary with subtitle'
    html_str, data, conflicted = merge_edit(origin_clean, user_clean, other_clean)
    html_str2, data2, conflicted2 = summary_edit([origin_clean, user_clean, other_clean])
    self.assertEquals(html_str, html_str2)
    data = [v for k, v in sorted(data.iteritems(), key=lambda o: o[0])]
    for oo in data:
        for o in oo:
            o['count'] = 1
    for oo in data2:
        for o in oo:
            del o['authors']
    self.assertEquals(data, data2)
    self.assertEquals(conflicted, conflicted2)

    user_clean = 'In this section, we explore the feasibility of compiling video augmented dictionary for learners from subtitles'
    html_str, data, conflicted = merge_edit(origin_clean, user_clean, other_clean)


if __name__ == "__main__":
  unittest.main()
