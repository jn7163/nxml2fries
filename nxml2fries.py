''' This script generates a fries standoff file format by building on top of
nxml2txt output'''

import sys
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
    indices = [span[0]]
    for s in staging: indices.extend((s[0]-1, s[1]+1))
    indices.append(span[1]+1)

    ranges = [(indices[i-1], indices[i]) for i in xrange(1,len(indices), 2)]

    # Return the filtered string
    return ''.join(txt[r[0]:r[1]] for r in ranges)


# Read the text file
with open(sys.argv[1]) as f:
    txt = f.read()

# Read the standoff file
with open(sys.argv[2]) as f:
    soff = f.readlines()

keep = ('article-title', 'abstract', 'sec', 'title', 'fig', 'p', 'supplementary-material')
remove = ('xref')

# Compute the spans of the citations to remove them from the text
citations = []

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

    elif tag in ('sec', 'fig', 'supplementary-material'):
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
        else:
            raise Exception("I shouldn't be here")

        # Add this section to the sections stack
        secs.append((sec, sec_norm))

        # Remember the current span
        current_span = (start, end)

    elif tag in ('title', 'p'):

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

            print '%i\t%s\t%s\t%i\t%s' % (ix, sec, sec_norm, 1 if tag == 'title' else 0, get_text(txt, start, end, citations))
