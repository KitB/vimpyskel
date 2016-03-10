import getpass
import os
import re
import sre_parse

import vim


class VPSContext(object):
    def __init__(self):
        self.templates = []

    def prepare(self):
        try:
            template_dir = vim.vars['vimpyskel_template_dir']
        except KeyError:
            template_dir = '~/.vim/skeletons'
        template_dir = os.path.realpath(os.path.expanduser(template_dir))

        self.templates.extend(get_templates(template_dir))

    def find_template(self, filepath):
        return most_specific_template(filepath, self.templates)

    def __call__(self):
        filepath = vim.current.buffer.name
        try:
            output = self.find_template(filepath)
        except TypeError:
            return

        if output is None:
            return

        template, match = output

        context = make_format_context(filepath, match)
        to_go_in_buffer = template.format(**context)

        del vim.current.buffer[:]
        vim.current.buffer.append(to_go_in_buffer.splitlines())
        del vim.current.buffer[0]


def make_format_context(filepath, match):
    context = {'filepath': filepath,
               'basename': os.path.basename(filepath),
               'dirpath': os.path.dirname(filepath),
               'dirname': os.path.basename(os.path.dirname(filepath)),
               'whoami': getpass.getuser(),
               'groups': match.groups(),
               }

    return context


def regex_specificity(regex, search_string):
    match = regex.search(search_string)

    if not match:
        return None

    ld1 = ld(regex.pattern, match.group(0))
    ld2 = ld(match.group(0), search_string)
    score = max(ld1, ld2)
    for t, v in sre_parse.parse(regex.pattern):
        if t == 'at':      # anchor...
            if v == 'at_beginning' or 'at_end':
                score -= 1   # ^ or $, adj 1 edit

            if v == 'at_boundary':  # all other anchors are 2 char
                score -= 2

    return score, match


def most_specific_template(filepath, templates):
    scores = []
    for template_re, template in templates:
        print template_re.pattern
        try:
            score, match = regex_specificity(template_re, filepath)
        except TypeError:
            continue
        print score
        if score is not None:
            scores.append((score, template, match))

    try:
        _, template, match = min(scores)
    except ValueError:
        return None
    else:
        return template, match


def read_template(template_str):
    template_regex_string, template_str = template_str.split('\n', 1)
    return (re.compile(template_regex_string), template_str)


def get_templates(template_dir):
    templates = (os.path.join(template_dir, filename) for filename in os.listdir(template_dir))
    templates = (filename for filename in templates if os.path.isfile(filename))

    out = []

    for filename in templates:
        with open(filename, 'r') as template_file:
            out.append(read_template(template_file.read()))

    return out


def ld(a, b):
    "Calculates the Levenshtein distance between a and b."
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a, b = b, a
        n, m = m, n

    current = range(n+1)
    for i in range(1, m + 1):
        previous, current = current, [i]+[0]*n
        for j in range(1, n + 1):
            add, delete = previous[j] + 1, current[j - 1] + 1
            change = previous[j - 1]
            if a[j - 1] != b[i - 1]:
                change = change + 1
            current[j] = min(add, delete, change)
    return current[n]
