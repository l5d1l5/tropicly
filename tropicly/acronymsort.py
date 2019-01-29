import re
import sys


def acronym_sort(content):
    """
    Sorts a list of Latex acronyms. For the list of acronyms, the acronym (V1.41) CTAN
    package syntax should be used. Furthermore, each line should contain only one acronym.
    The algorithm sorts only acronyms rest of the document is left untouched.

    :param content: list of str
        A list of string.
    :return: list of str
        A list of string.
    """
    # Latex acronym "any\acro{letter|number| |-}{letter|number| |-}\n"
    acronym_grammar = re.compile(r'(^.*\\acro\{(?P<acronym>[\w+ -]+)\}\{[\w/ -]+\}\r?\n?$)')

    lines = []
    count = 0
    while count < len(content):
        line = content[count]
        match = acronym_grammar.match(line)

        if match:
            acronym_lines = []
            while match:
                acronym_lines.append(match)

                count += 1
                line = content[count]
                match = acronym_grammar.match(line)

            acronym_lines = sorted(acronym_lines, key=lambda obj: obj.group('acronym'))
            lines += [obj.group(1) for obj in acronym_lines]

        else:
            lines.append(line)
            count += 1

    return lines


if __name__ == '__main__':
    # from cli: first in  file and second arg out file
    in_name = sys.argv[1]
    out_name = sys.argv[2]

    with open(in_name, 'r') as src:
        out = acronym_sort(src.readlines())

        with open(out_name, 'w') as dst:
            dst.writelines(out)
