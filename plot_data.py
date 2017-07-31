#!/usr/bin/python3
import matplotlib.pyplot as plt
import sys, os
import numpy as np
import traceback
import re

# plot basic line graph
# assume that data is stored in .+_[0-9]+.out files
# each file represent a point in the plot
# y value is calculated by the data in the files
# x value is extracted from filename

# the line contains the same type data but in multiple times
# this function is to parse the line and return the average data
def process_content(content):
    sum = 0
    count = 0
    for line in content:
        if 'Completed' in line:
            token = line[line.find('Completed'):].split(' ')
            sum += float(token[1])
            count += 1
    return sum / count

def load(in_file, st_idx, end_idx):
    file_list = []
    for i in range(st_idx, end_idx + 1):
        if not os.path.isfile(in_file + '_' + str(i) + '.out'):
            print('no such file named:', in_file + '_' + str(i) + '.out')
            continue
        with open(in_file + '_' + str(i) + '.out', 'r') as f:
            content = f.readlines()
        file_list.append((i, content))
    ret = [ (x, process_content(content)) for x, content in file_list ]
    # print(ret)
    return tuple(map(list, zip(*ret)))


def plot(x, y, out_file):
    plt.plot(x, y)
    plt.xlim(max(x), min(x))
    # plt.savefig(out_file + '.eps')
    plt.show()

def set_tick(plt, xs):
    xticks = max(xs, key=len)
    xticks = [1,2,4,8,12,16,24]
    if xticks:
        plt.xticks(xticks)

def scala_tn_special(xs, ys):
    # return list(zip(*[ (x, y) if x[0] == 1 else (x, [ yi * 2 for yi in y ]) for x, y in zip(xs, ys) ]))
    return list(zip(*[ (x, y) if x[0] == 1 else ([ xi // 2 for xi in x ], y) for x, y in zip(xs, ys) ]))

line_markers = [ 'o', 'v', '^', '*', 'x', '.', '>', ',', '+', '<', 'D', 'p' ]
def multi_plot(xs, ys, out_file, paths, reversed, xlabel, ylabel):
    global line_markers
    xs, ys = scala_tn_special(xs, ys)
    xs = list(xs)
    ys = list(ys)
    if reversed:
        plt.xlim(max(xs[0]), min(xs[0]))
    lines = []
    for x, y, label, marker in zip(xs, ys, paths, line_markers):
        line, = plt.plot(x, y, label=label, marker=marker)
        lines.append(line)
    legend = plt.legend(handles=lines, loc=1)

    set_tick(plt, xs)

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    if out_file == '0':
        plt.show()
    else:
        plt.savefig(out_file + '.eps')

def multi_print(xs, ys, paths):
    for x, y, label in zip(xs, ys, paths):
        print(label,'========================================')
        for xi, yi in zip(x, y):
            print(xi, '\t', yi)

def remove_common_in_path(paths):
    common_part = set()
    wlists = []
    for path in paths:
        wlist = re.sub('[^\w]', ' ', path).split()
        wlists.append(wlist)
        common_part |= set(wlist)
    for wlist in wlists:
        common_part &= set(wlist)
    for wlist in wlists:
        for w in common_part:
            wlist.remove(w)
    return [ '-'.join(wlist) for wlist in wlists ]

# def extract_parent(paths):
    # return [ ' '.join(path.split('/')[-3:-1]) for path in paths ]


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('usage: <reversed> <path-of-data-1> <path-of-data-2> ... <input-filename-without-suffix> <start-x> <end-x> <output-filename-without-suffix> <xlabel> <ylabel>')
        sys.exit(0)
    reversed = int(sys.argv[1])
    # the path of data
    paths = sys.argv[2:-6]
    # the same name of input files
    in_file = sys.argv[-6]
    # the start suffix name of input files
    st_idx = int(sys.argv[-5])
    # the end suffix name of input files
    end_idx = int(sys.argv[-4])
    # the name of output file
    out_file = sys.argv[-3]
    # the name of x label
    xlabel = sys.argv[-2]
    # the name of y label
    ylabel = sys.argv[-1]
    mypath = os.path.realpath(__file__)
    mypath = os.path.dirname(mypath)
    xs, ys = ([], [])
    for path in paths:
        os.chdir(path)
        try:
            x, y = load(in_file, st_idx, end_idx)
        except:
            traceback.print_exc()
            print(path)
            exit(1)
        xs.append(x)
        ys.append(y)
        os.chdir(mypath)
    multi_plot(xs, ys, out_file, remove_common_in_path(paths), reversed, xlabel, ylabel)
    multi_print(xs, ys, remove_common_in_path(paths))
