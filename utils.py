# encoding=utf8
import codecs
import csv
import re
from collections import defaultdict

import fire


def remove_tone_file(in_path, out_path):
    with codecs.open(in_path, 'r', encoding='utf-8') as in_file, \
            codecs.open(out_path, 'w', encoding='utf-8') as out_file:
        for line in in_file:
            utf8_line = line
            no_tone_line = remove_tone_line(utf8_line)
            try:
                out_file.write(no_tone_line)
            except UnicodeDecodeError as e:
                print('Line with decode error:')
                print(e)


def decompose_predicted_test_file(in_path, out_no_tone_path=None, out_simplified_path=None):
    """
    Convert a predicted test file to two files:
        1. a csv file with line_and_word_id and no tone word
        2. a csv file with line_and_word_id and simplified word
    :param in_path: path to in put file
    :return: None, write to files
    """
    removed_ext_path = in_path.rsplit('.', 1)[0]
    if out_no_tone_path is None:
        out_no_tone_path = removed_ext_path + '_no_tone.csv'
    if out_simplified_path is None:
        out_simplified_path = removed_ext_path + '_simplified.csv'

    no_tone_header = ['id', 'no_tone']
    simplified_header = ['id', 'label']
    with codecs.open(in_path, 'r', encoding='utf-8') as in_file, \
            open(out_no_tone_path, 'w') as out_no_tone_file, \
            open(out_simplified_path, 'w') as out_simplified_file:

        out_no_tone_writer = csv.writer(out_no_tone_file, delimiter=',')
        out_simplified_writer = csv.writer(out_simplified_file, delimiter=',')

        out_no_tone_writer.writerow(no_tone_header)
        out_simplified_writer.writerow(simplified_header)

        for line in in_file:
            no_tone_words, simplified_words = process_line(line)
            if len(simplified_words) < 1000:
                write_to_test_label(out_no_tone_writer, no_tone_words[0], no_tone_words[1:])
                write_to_test_label(out_simplified_writer, no_tone_words[0], simplified_words[1:])

    assert count_lines(out_simplified_path) == count_lines(out_no_tone_path)


def rematch(test_words, output_words, detone_output_words):
    if len(output_words) == 0:
        return [0] * len(test_words)

    if len(test_words) == 0:
        return []

    f = defaultdict(int)
    trc = {}
    is_match = defaultdict(bool)

    # DP
    for i_test in range(len(test_words)):
        for i_out in range(len(detone_output_words)):
            f[i_test, i_out] = f[i_test - 1, i_out]
            trc[i_test, i_out] = (-1, 0)

            if f[i_test, i_out] < f[i_test, i_out - 1]:
                f[i_test, i_out] = f[i_test, i_out - 1]
                trc[i_test, i_out] = (0, -1)

            match = test_words[i_test] == detone_output_words[i_out]
            if f[i_test, i_out] < f[i_test - 1, i_out - 1] + int(match):
                f[i_test, i_out] = f[i_test - 1, i_out - 1] + int(match)
                trc[i_test, i_out] = (-1, -1)
                is_match[i_test, i_out] = match

    # Trace
    i_test = len(test_words) - 1
    i_out = len(detone_output_words) - 1
    res = []
    while i_test >= 0 and i_out >= 0:
        move = trc[i_test, i_out]
        if is_match[i_test, i_out]:
            res.append(output_words[i_out])
        elif move[0] == -1:
            res.append(0)
        i_test += move[0]
        i_out += move[1]

    res += [0] * (i_test+1)

    assert len(res) == len(test_words)
    return list(reversed(res))


def rematch_greedy(test_words, output_words, detone_output_words):
    test_words.append('<EOS>')
    output_words.append(0)
    detone_output_words.append('<EOS>')
    l_test = len(test_words)
    res = [output_words[0]]
    o_id = 1
    t_id = 1
    while t_id < l_test:
        if test_words[t_id] != detone_output_words[o_id]:
            if test_words[t_id+1] == detone_output_words[o_id]:
                res.append(output_words[o_id-1] if test_words[t_id] == detone_output_words[o_id-1] else 0)
                t_id += 1
            else:
                o_id += 1
        else:
            res.append(output_words[o_id])
            o_id += 1
            t_id += 1
        if o_id >= len(output_words):
            break
    if len(res) < l_test:
        res += [0] * (l_test - len(res))
    elif len(res) > l_test:
        res = res[:l_test]
    assert len(res) == l_test
    return res[:-1]


def post_process(presub='presub.txt', sub='submission.txt', test='input/test.txt'):
    simplified_header = ['id', 'label']
    with codecs.open(presub, 'r', encoding='utf-8') as in_file, \
            open(sub, 'w') as out_simplified_file, open(test, 'r') as test_file:

        test_lines = {}
        for test_line in test_file:
            test_lines[test_line.split(',')[0]] = test_line

        out_simplified_writer = csv.writer(out_simplified_file, delimiter=',')

        out_simplified_writer.writerow(simplified_header)

        for line in in_file:
            no_tone_words, simplified_words = process_line(line)
            test_line = test_lines[no_tone_words[0]]
            test_words = process_line_no_detone(test_line)
            if len(simplified_words) < 1000:
                # write_to_test_label(out_no_tone_writer, no_tone_words[0], no_tone_words[1:])
                if len(test_words) != len(simplified_words):
                    print('%d != %d' % (len(test_words), len(simplified_words)))
                    simplified_words = rematch(test_words, simplified_words, no_tone_words)
                write_to_test_label(out_simplified_writer, no_tone_words[0], simplified_words[1:])


def remove_tone_line(utf8_str):
    intab_l = "ạảãàáâậầấẩẫăắằặẳẵóòọõỏôộổỗồốơờớợởỡéèẻẹẽêếềệểễúùụủũưựữửừứíìịỉĩýỳỷỵỹđ"
    intab_u = "ẠẢÃÀÁÂẬẦẤẨẪĂẮẰẶẲẴÓÒỌÕỎÔỘỔỖỒỐƠỜỚỢỞỠÉÈẺẸẼÊẾỀỆỂỄÚÙỤỦŨƯỰỮỬỪỨÍÌỊỈĨÝỲỶỴỸĐ"
    intab = intab_l + intab_u

    outtab_l = "a" * 17 + "o" * 17 + "e" * 11 + "u" * 11 + "i" * 5 + "y" * 5 + "d"
    outtab_u = "A" * 17 + "O" * 17 + "E" * 11 + "U" * 11 + "I" * 5 + "Y" * 5 + "D"
    outtab = outtab_l + outtab_u

    r = re.compile("|".join(intab))
    replaces_dict = dict(zip(intab, outtab))

    return r.sub(lambda m: replaces_dict[m.group(0)], utf8_str)


def normalize_tone_line(utf8_str):
    # The following lines should contain éè instead of èé, yet ground truth was probably generated by this as well
    intab_l = "áàảãạâấầẩẫậăắằẳẵặđèéẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵ"
    intab_u = "ÁÀẢÃẠÂẤẦẨẪẬĂẮẰẲẴẶĐÈÉẺẼẸÊẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴ"
    intab = intab_l + intab_u

    outtab_l = [
        "a1", "a2", "a3", "a4", "a5",
        "a6", "a61", "a62", "a63", "a64", "a65",
        "a8", "a81", "a82", "a83", "a84", "a85",
        "d9",
        "e1", "e2", "e3", "e4", "e5",
        "e6", "e61", "e62", "e63", "e64", "e65",
        "i1", "i2", "i3", "i4", "i5",
        "o1", "o2", "o3", "o4", "o5",
        "o6", "a61", "o62", "o63", "o64", "o65",
        "o7", "o71", "o72", "o73", "o74", "o75",
        "u1", "u2", "u3", "u4", "u5",
        "u7", "u71", "u72", "u73", "u74", "u75",
        "y1", "y2", "y3", "y4", "y5",
    ]

    outtab_u = [
        "A1", "A2", "A3", "A4", "A5",
        "A6", "A61", "A62", "A63", "A64", "A65",
        "A8", "A81", "A82", "A83", "A84", "A85",
        "D9",
        "E1", "E2", "E3", "E4", "E5",
        "E6", "E61", "E62", "E63", "E64", "E65",
        "I1", "I2", "I3", "I4", "I5",
        "O1", "O2", "O3", "O4", "O5",
        "O6", "O61", "O62", "O63", "O64", "O65",
        "O7", "O71", "O72", "O73", "O74", "O75",
        "U1", "U2", "U3", "U4", "U5",
        "U7", "U71", "U72", "U73", "U74", "U75",
        "Y1", "Y2", "Y3", "Y4", "Y5",
    ]

    r = re.compile("|".join(intab))
    replaces_dict = dict(zip(intab, outtab_l + outtab_u))

    return r.sub(lambda m: replaces_dict[m.group(0)], utf8_str)


def _remove_special_chars_and_numbers(unicode_line):
    removed_special_chars = re.sub('[^a-zA-Z\d\\\\]', ' ', repr(unicode_line))[1:]
    removed_numbers = re.sub(r'\b\d+\b', '', removed_special_chars)
    return removed_numbers


def write_to_test_label(label_writer, line_id, words):
    for i, word in enumerate(words):
        line = ['{}{:03}'.format(line_id, i), word]
        label_writer.writerow(line)


def process_line_no_detone(line):
    line = line.strip('\n')

    no_tone_line_alphanumeric = re.sub('[^a-zA-Z\d]', ' ', repr(line))

    no_tone_words = no_tone_line_alphanumeric.split()

    filtered_no_tone_words = []
    for i, word in enumerate(no_tone_words):
        if not word.isalpha():
            continue
        filtered_no_tone_words.append(word)

    return filtered_no_tone_words


def process_line(line):
    """
    Process a line
    :param line:
    :return: no_tone_line, no_tone_words, simplified_words
    """
    utf8_line = line
    utf8_line = utf8_line.strip('\n')

    no_tone_line_pre = remove_tone_line(utf8_line)
    normalized_line_pre = normalize_tone_line(utf8_line)

    no_tone_line_alphanumeric = re.sub('[^a-zA-Z\d]', ' ', repr(no_tone_line_pre))
    normalized_line_alphanumeric = re.sub('[^a-zA-Z\d]', ' ', repr(normalized_line_pre))

    no_tone_words = no_tone_line_alphanumeric.split()
    normalized_words = normalized_line_alphanumeric.split()
    assert len(no_tone_words) == len(normalized_words)

    filtered_no_tone_words = []
    simplified_words = []
    for i, word in enumerate(no_tone_words):
        if not word.isalpha():
            continue
        simplified_word = simplify(normalized_words[i])
        if simplified_word == '#':
            continue
        filtered_no_tone_words.append(word)
        simplified_words.append(simplified_word)

    return filtered_no_tone_words, simplified_words


def simplify(word):
    """
    normalize and simplify a vni word:
    * move tone digit to the end
    * return only digits
    * return 0 if there is no digit
    """
    if word.isalpha():
        return '0'
    ret = ''
    tone = ''
    for letter in word:
        if '1' <= letter <= '9':
            if '1' <= letter <= '5':
                # assert len(tone) == 0, '{}, {}'.format(tone, word)
                if tone != '':
                    return '#'  # ignore this word
                tone = letter
            else:
                ret += letter
    return ret + tone


def count_lines(thefilepath):
    count = 0
    for _ in open(thefilepath):
        count += 1
    return count


def get_ids(file_path):
    ids = set()
    with codecs.open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            ids.add(line[:3])
    return ids


def compare_ids(file1, file2):
    """
    compare ids between two files
    """
    ids1 = get_ids(file1)
    ids2 = get_ids(file2)

    print('ids in {} but not in {}:'.format(file1, file2))
    print(ids1 - ids2)
    print('ids in {} but not in {}:'.format(file2, file1))
    print(ids2 - ids1)


if __name__ == '__main__':
    fire.Fire()
