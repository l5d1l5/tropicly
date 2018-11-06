"""
acrosort.py

Author: Tobias Seydewitz
Date: 06.11.18
Mail: tobi.seyde@gmail.com
"""
import re
import sys


def acrosort(content):
    regex = re.compile(r'(^.*\\acro\{(?P<acro>[\w+ -]+)\}\{[\w/ -]+\}\r?\n?$)')

    lines = []
    count = 0
    while count < len(content):
        line = content[count]
        match = regex.match(line)

        if match:
            acros = []
            while match:
                acros.append(match)
                count += 1
                line = content[count]
                match = regex.match(line)

            acros = sorted(acros, key=lambda obj: obj.group('acro'))
            lines += [obj.group(1) for obj in acros]

        else:
            lines.append(line)
            count += 1

    return lines


if __name__ == '__main__':
    in_name = sys.argv[1]
    out_name = sys.argv[2]

    handler = open(in_name, 'r')
    out = acrosort(handler.readlines())

    with open(out_name, 'w') as dst:
        dst.writelines(out)
