''' This script generates a fries standoff file format by building on top of
nxml2txt output'''

import sys
import itertools as it

nil = 'N/A'

def span_contains(parent, child):
    ''' Returns wether parent contains child '''

    return True if parent[0] <= child[0] and parent[1] >= 1 else False

# Read the text file
# with open(sys.argv[1]) as f:
#     txt = f.read()

# Read the standoff file
with open(sys.argv[2]) as f:
    soff = f.readlines()

keep = ('article-title', 'abstract', 'sec', 'title', 'fig', 'p', 'supplementary-material')

entries = (s for s in soff if s.split('\t', 2)[1].split()[0] in keep) # Keep only the lines that correspond to a tag in 'keep'

secs = [] # Stack of sections
title_seen = False
sm = fig = 1

for ix, e in enumerate(entries):

    # Parse the line
    _, t_r, __, attrs = e.split('\t')
    tag, start, end = t_r.split(' ')

    if tag in ('article-title', 'abstract'):

        # This is to enforce only one "article-title" (the actual title of the paper tag per file.
        # There are other instance of the tag in the references

        if tag == 'article-title':
            if title_seen:
                continue
            else:
                title_seen = True

        print '%i\t%s\t%s\t%i\t%s %s' % (ix, nil, tag, 1 if tag == 'article-title' else 0, start, end)

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

            print '%i\t%s\t%s\t%i\t%s %s' % (ix, sec, sec_norm, 1 if tag == 'title' else 0, start, end)
