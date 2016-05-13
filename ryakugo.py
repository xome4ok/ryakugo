# -*- coding: utf-8 -*-
from __future__ import division
import io, re
from cjktools.resources import auto_format
from collections import Counter


def see_also(edict2_item):
    abbr = [s for s in edict2_item.senses if s.__contains__('(abbr)')][0]
    sea = re.search(r'\(See (.*?)\)', abbr)
    if sea is None:
        return None
    fish = sea.group(1)
    return fish


def jap_word_length(w):
    stop = ur"[ゃょゅュャョ]"
    only_big_kana = re.sub(stop, '', w)
    return len(only_big_kana)


def take_first_word_only(s):
    # just split string on ; and take first part
    k = s.split(";")[0]
    return re.sub("\(.*\)","",k).strip()

EDICT_PATH = "/home/xome4ok/.cjkdata/dict/je_edict"
RYAKUGO_PATH = "/home/xome4ok/.cjkdata/dict/je_ryakugo"
EDICT2_PATH = "/home/xome4ok/.cjkdata/dict/je_edict2"
RYAKUGO2_PATH = "/home/xome4ok/.cjkdata/dict/je_ryakugo2"


def load_dict(path):
    with io.open(path, encoding='utf-8') as edict_file:
        dict = auto_format.load_dictionary(edict_file)
        return dict


def length_by_word(ryaku_dict, length_function=jap_word_length):
    jap_length_by_word = []
    for word in ryaku_dict:
        found = ryaku_dict[word]
        first_reading = take_first_word_only(found.readings[0])
        jap_length_by_word.append(
            {
                'word': take_first_word_only(word), 
                'reading': first_reading,
                'length': length_function(first_reading)
            }
             )
    return jap_length_by_word


def count_of_lengths(length_by_word_list):
    count = Counter()
    for item in length_by_word_list:
        count[item['length']] +=1
    return count


def most_common16(count):
    return count.most_common(16)


def most_common_freqs(count, ryakugo_dict):
    return list(map(lambda x: (x[0], x[1]/len(ryakugo_dict)), most_common16(count)))


# only for edict2
def length_of_related_word(ryakugo_dict2_item, full_edict2, length_function=jap_word_length):
    related = see_also(ryakugo_dict2_item)
    if related in full_edict2:
        found = take_first_word_only(full_edict2[related].readings[0])
        return {'word': take_first_word_only(full_edict2[related].word),
                'reading': found, 
                'length': length_function(found)}
    else:
        return None


# only for edict2, 4-7 is the most frequent occurence
def abbr_and_related_word_readings(len_with_rel, len_of_abbr=4, len_of_rel=7):
    return [(x[0], x[2]) for x in jap_lwr]


# only for edict2
def length_with_related(ryaku_dict, full_edict2, length_function=jap_word_length):
    jap_length_by_word = []
    for word in ryaku_dict:
        found = ryaku_dict[word]
        lorw = length_of_related_word(found, full_edict2, length_function)
        if lorw is not None:
            first_reading = take_first_word_only(found.readings[0])
            jap_length_by_word.append(
                {'abbr_word': take_first_word_only(word),
                 'abbr_reading':first_reading,
                 'abbr_length':length_function(first_reading),
                 'source_word':lorw['word'],
                'source_reading':lorw['reading'],
                'source_length':lorw['length']}
                 )
    return jap_length_by_word


def matrix_of_related_lengths(lwr):
    M = Counter()
    for item in lwr:
        M[(item['source_length'],item['abbr_length'])] += 1
    return dict(M)


d = load_dict(RYAKUGO2_PATH)
edict = load_dict(EDICT2_PATH)

japanese_length_by_word = length_by_word(d)
#casual_length_by_word = length_by_word(d, length_function=len)
jap_count = count_of_lengths(japanese_length_by_word)
#casual_count = count_of_lengths(casual_length_by_word)
mcf_j = most_common_freqs(jap_count, d)
#mcf_c = most_common_freqs(casual_count, d)
#print most_common16(jap_count)
#print most_common16(casual_count)
#print ""
#print most_common_freqs(jap_count, d)
#print most_common_freqs(casual_count, d)

jap_lwr = length_with_related(d, edict)
matrix_lwr = matrix_of_related_lengths(jap_lwr)
#casual_lwr = length_with_related(d, edict, length_function=len)