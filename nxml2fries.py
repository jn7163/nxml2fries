''' This script generates a fries standoff file format by building on top of
nxml2txt output'''

import argparse
import itertools as it

nil = 'N/A'

def span_contains(parent, child):
    ''' Returns wether parent contains child '''

    return True if parent[0] <= child[0] and parent[1] >= child[1] else False

def get_text(txt, start, end, citations):
    ''' Returns a string with the text within start-end removing all the text within any of the ranges in citations '''

    span = (start, end)

    staging = [s for s in citations if span_contains(span, s)]

    # Calculate the ranges to include

    for s in staging:
        s = list(s)
        snippet = txt[s[0]:s[1]]

        open_parenthesis = False

        if not snippet[0] in ('[', '('):
            if txt[s[0]-1] in ('[', '('):
                s[0] -= 1
                open_parenthesis = True

        if not snippet[-1] in (']', ')'):
            if s[1] < len(txt) and txt[s[1]] in (']', ')'):
                s[1] += 1
            elif open_parenthesis:
                # This is the case in which we're looking for a matching right bracket
                for i in xrange(1, len(txt) - s[1]):
                    if txt[s[1]+i] in (']', ')') and (s[1] + i) < len(txt):
                        s[1] += i + 1
                        break

        txt = txt[:s[0]] + ' ' * (s[1] - s[0]) + txt[s[1]:]

    # These lines replaces the new-line characters for spaces
    ret = txt[start:end+1]
    ret = ret.replace('\n', ' ')

    return ret

def parse_args():
    parser = argparse.ArgumentParser(description='parse nxml file and dump sections')
    parser.add_argument('--no-citations', action='store_true', dest='no_citations', help='replace citations with spaces')
    parser.add_argument('--no-header', dest='header', action='store_false', help="don't include column header")
    parser.add_argument('textfile', help='text file')
    parser.add_argument('standoff', help='standoff file')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()

    # Read the text file
    with open(args.textfile) as f:
        txt = f.read()

    # Read the standoff file
    with open(args.standoff) as f:
        soff = f.readlines()

    # print column headers if required
    if args.header:
        print 'chunk_id\tsection_id\tname\tis_title\ttext'

    keep = ('article-title', 'abstract', 'sec', 'title', 'fig', 'p', 'supplementary-material', 'ref-list', 'ref')
    remove = ('xref', 'table')

    # Compute the spans of the citations to remove them from the text
    citations = []

    if args.no_citations:
        for line in (s for s in soff if s.split('\t', 2)[1].split()[0] in remove):
            # Parse the line
            _, t_r, __ = line.split('\t', 2)

            _, start, end = t_r.split(' ')

            start, end = int(start), int(end)

            if start != end:
                citations.append((start, end))

    # Keep only the lines that correspond to a tag in 'keep'
    entries = (s for s in soff if s.split('\t', 2)[1].split()[0] in keep)

    secs = [] # Stack of sections
    title_seen = False
    sm = fig = 1

    for ix, e in enumerate(entries):

        # Parse the line
        _, t_r, __, attrs = e.split('\t')
        tag, start, end = t_r.split(' ')
        start = int(start)
        end = int(end)

        if tag in ('article-title', 'abstract'):

            # This is to enforce only one "article-title" (the actual title of the paper tag per file.
            # There are other instance of the tag in the references

            if tag == 'article-title':
                if title_seen:
                    continue
                else:
                    title_seen = True

            print '%i\t%s\t%s\t%i\t%s' % (ix, nil, tag, 1 if tag == 'article-title' else 0, get_text(txt, start, end, citations))

        elif tag in ('sec', 'fig', 'supplementary-material', 'ref-list'):
            # For our purposes, sections and figures are equivalent

            # Parse the attributes
            attrs = {k:v.strip('"') for k, v in ((s.split('=') for s in attrs.split()))}

            # Figure out the section id
            if tag == 'sec':
                sec = attrs['id'] if 'id' in attrs else nil
                sec_norm = attrs['sec-type'] if 'sec-type' in attrs else nil
            elif tag == 'fig':
                sec = 'fig-%i' % fig
                sec_norm = sec
                fig += 1
            elif tag == 'supplementary-material':
                sec = 'supm-%i' % sm
                sec_norm = sec
                sm += 1
            elif tag == 'ref-list':
                sec = 'references'
                sec_norm = sec
            else:
                raise Exception("I shouldn't be here")

            # Add this section to the sections stack
            secs.append((sec, sec_norm))

            # Remember the current span
            current_span = (start, end)

        elif tag in ('title', 'p', 'ref'):

            # Only if we are in a section or image, otherwise this could be part of the references or metadata
            if len(secs) > 0:

                if span_contains(current_span, (start, end)):
                    # If the current section's span contains this element
                    sec, sec_norm = secs[-1]
                else:
                    # Pop the current section to return to the previous onse
                    secs.pop()
                    if len(secs) > 0:
                        sec, sec_norm = secs[-1]
                    else:
                        # If there are no more sections in the stack, this element may not be useful information
                        continue

                text = get_text(txt, start, end, citations)

                if tag == 'ref':
                    text = text.replace('\n', ' ')

                print '%i\t%s\t%s\t%i\t%s' % (ix, sec, sec_norm, 1 if tag == 'title' else 0, text)
