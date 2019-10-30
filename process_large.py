import random

import fire
from tqdm import tqdm

from utils import remove_tone_line


def run(corpus='/home/vietai/wd8/vn-news/corpus-full.txt',
        train_d='./input/train_large.d',
        train_t='./input/train_large.t',
        dev_d='./input/dev_large.d',
        dev_t='./input/dev_large.t',
        exclude='./input/test.d',
        dev_prob=10000.0/111000000):
    input_file = open(corpus, 'r')
    train_d_file = open(train_d, 'w')
    train_t_file = open(train_t, 'w')
    dev_d_file = open(dev_d, 'w')
    dev_t_file = open(dev_t, 'w')
    to_exclude = set()
    with open(exclude, 'r') as f:
        for line in f:
            to_exclude.add(line.strip().lower())
    print('%d sentences from %s' % (len(to_exclude), exclude))

    ex_cnt = 0
    cnt = 0
    for line in tqdm(input_file):
        cnt += 1
        t_line = line.strip()
        d_line = remove_tone_line(t_line)
        if d_line.lower() in to_exclude:
            ex_cnt += 1
            continue
        if random.random() < dev_prob:
            # Write to dev
            dev_d_file.write(d_line + '\n')
            dev_t_file.write(t_line + '\n')
        else:
            # Write to train
            train_d_file.write(d_line + '\n')
            train_t_file.write(t_line + '\n')

    print('%d/%d sentences excluded' % (ex_cnt, cnt))

    input_file.close()
    train_d_file.close()
    train_t_file.close()
    dev_d_file.close()
    dev_t_file.close()


if __name__ == '__main__':
    fire.Fire(run)
