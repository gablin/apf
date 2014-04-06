#!/usr/bin/python

#=========
# IMPORTS
#=========

import string
import sys



#================
# HELP FUNCTIONS
#================

def reportError(msg):
    sys.stderr.write("ERROR at line " + str(i) + ":\n")
    sys.stderr.write(msg + "\n")
    sys.exit(1)

def isAtChapterSeparator(s):
    if len(s) == 0:
        return False
    for c in s:
        if c != '-':
            return False
    return True

def isAtChapterName(s):
    return len(s) >= 5 and s[0:4] == "*** "

def extractChapterName(s):
    if len(s) < 5:
        reportError("Invalid chapter syntax");
    return s[4:].strip()

def isAtSectionName(s):
    if len(s) == 0 or s[0] == ' ':
        return False
    for c in s:
        if string.letters.find(c) > -1 and not string.uppercase.find(c) > -1:
            return False
    return True

def extractSectionName(s):
    return s[0] + s[1:].strip().lower()

def checkSpacesExact(s, num):
    return len(s) > num + 1 and s[0:num] == " " * num and s[num] != ' '

def checkSpacesAtLeast(s, num):
    return len(s) > num + 1 and s[0:num] == " " * num

def isAtIndentedText(s):
    return checkSpacesExact(s, 6)

def isAtIndentedTextContinue(s):
    return checkSpacesAtLeast(s, 8)

def isAtTextExcerpt(s):
    return checkSpacesExact(s, 8)

def isAtTextExcerptContinue(s):
    return checkSpacesAtLeast(s, 10)

def isAtQuote(s):
    return len(s) > 2 and (s[0] == '-' or s[0] == '+') and s[1] == ' '

def isAtQuoteContinue(s):
    return checkSpacesExact(s, 2)

def isAtQuoteDescription(s):
    return checkSpacesExact(s, 2)

def isAtQuoteDescriptionContinue(s):
    return checkSpacesExact(s, 2)

def isAtEmptyLine(s):
    return len(s) == 0

def replace(s, m_start, m_end, t_start, t_end):
    sep_chars = " '\",."
    new_s = ""
    i = 0
    while True:
        start_pos = s.find(m_start, i)
        if start_pos <= -1:
            break
        must_be_within_same_word = (m_start == m_end
                                    and start_pos != 0
                                    and sep_chars.find(s[start_pos - 1]) <= -1)
        end_pos = s.find(m_end, start_pos + len(m_start))
        if end_pos <= -1:
            break
        do_skip = False
        if end_pos > start_pos + len(m_start):
            if must_be_within_same_word:
                section = s[start_pos + len(m_start):end_pos]
                for c in sep_chars:
                    if section.find(c) > -1:
                        do_skip = True
                        break
            if not do_skip:
                new_s += (s[i:start_pos]
                          + t_start
                          + s[start_pos + len(m_start):end_pos]
                          + t_end)
        else:
            do_skip = True
        if do_skip:
            new_s += s[i:end_pos + len(m_end)]
        i = end_pos + len(m_end)
    new_s += s[i:]
    return new_s

def toLatex(s):
    s = s.replace("...", "\\ldots{}");
    s = replace(s, "_", "_", "\\emph{", "}")
    s = replace(s, "*", "*", "\\emph{", "}")
    s = replace(s, "<<", ">>", "\\footnote{", "}")
    # TODO: add missing replacements
    return s

def typesetDeath(s):
    new_s = ""
    offset = 0
    i = offset
    while i < len(s):
        start_of_smallcaps = s[i].isalpha() and s[i].isupper()
        i += 1
        if start_of_smallcaps:
            j = i
            k = j
            while k < len(s):
                is_uppercase = s[k].isalpha() and s[k].isupper()
                if is_uppercase:
                    j = k
                end_of_smallcaps = s[k].isalpha() and not s[k].isupper()
                k += 1
                if end_of_smallcaps:
                    break
            section = s[i-1:j+1]
            num_uppercase = 0
            for c in section:
                if c.isupper():
                    num_uppercase += 1
            if num_uppercase >= 3:
                section = section.lower()

                # Make 'I' into uppercase
                k = 0
                while k < len(section):
                    if (section[k] == 'i'
                        and (k < len(section) - 1
                             and not section[k + 1].isalpha())
                        and (k == 0
                             or not section[k - 1].isalpha())
                        ):
                        section = (section[:k]
                                   + section[k].upper()
                                   + section[k + 1:])
                    k += 1
                # Make first letter of new sentence uppercase
                k = 0
                while k < len(section):
                    if section[k] == '.':
                        if k < len(section) - 2 and section[k + 1] == ' ':
                            section = (section[:k + 2]
                                       + section[k + 2].upper()
                                       + section[k + 3:])
                            k += 3
                    else:
                        k += 1

                # Make all occurrances of 'Death' as title
                section = section.replace("death", "Death")

                new_s += s[offset:i - 1] + "\\textsc{" + section + "}"
            else:
                new_s += s[offset:j + 1]
            offset = j + 1
            i = offset
    new_s += s[offset:]
    return new_s

def extractQuoteParts(s):
    pos = s.find("] ")
    if pos < 0:
        reportError("Invalid quote syntax")
    return s[0:pos], s[pos+2:]



#=============
# MAIN SCRIPT
#=============

# Check input argument
if len(sys.argv) < 2:
    sys.stderr.write("No input file\n")
    sys.exit(1)
if len(sys.argv) > 2:
    sys.stderr.write("Too many arguments\n")
    sys.exit(1)

input_file = sys.argv[1]

# Read input file
with open(input_file) as f:
    content = f.readlines()

# Remove trailing whitespace
for i in range(len(content)):
    content[i] = content[i].rstrip()

# Produce copyright data
# TODO: implement

# Move to beginning of first chapter
i = 0
while True:
    line = content[i]
    if isAtChapterSeparator(line):
        break
    i += 1
    if i >= len(content):
        reportError("Beginning of first chapter not found")

# Process regular content
while i < len(content):
    if isAtChapterSeparator(content[i]):
        i += 1
        if isAtChapterName(content[i]):
            print "\\chapter{" + toLatex(extractChapterName(content[i])) + "}"
            i += 1
            if not isAtChapterSeparator(content[i]):
                reportError("Expected chapter separator not found")
            i += 1
        else:
            # At end of content
            break
    elif isAtSectionName(content[i]):
        print "\\section{" + toLatex(extractSectionName(content[i])) + "}"
        i += 1
    elif isAtIndentedText(content[i]):
        print "\\begin{indentText}"
        while i < len(content) and isAtIndentedText(content[i]):
            j = i + 1
            while j < len(content) and isAtIndentedTextContinue(content[j]):
                j += 1
            print ("\\indentItem{"
                   + toLatex(
                        " ".join([ content[k].strip() for k in range(i, j) ])
                     )
                   + "}")
            i = j
        print "\end{indentText}"
    elif isAtTextExcerpt(content[i]):
        print "\\begin{excerptText}"
        while i < len(content) and isAtTextExcerpt(content[i]):
            j = i + 1
            while j < len(content) and isAtTextExcerptContinue(content[j]):
                j += 1
            print ("\\excerptItem{"
                   + toLatex(
                        " ".join([ content[k].strip() for k in range(i, j) ])
                     )
                   + "}")
            i = j
        print "\end{excerptText}"
    elif isAtQuote(content[i]):
        j = i + 1
        while j < len(content) and isAtQuoteContinue(content[j]):
            j += 1
        pages, quote = extractQuoteParts(
                         " ".join([ content[k].strip() for k in range(i, j) ])
                       )
        print "\\apQuote{" + pages + "}{" + toLatex(typesetDeath(quote)) + "}"
        i = j
    elif isAtEmptyLine(content[i]):
        print
        i += 1
    elif isAtQuoteDescription(content[i]):
        j = i + 1
        while j < len(content) and isAtQuoteDescriptionContinue(content[j]):
            j += 1
        print toLatex(" ".join([ content[k].strip() for k in range(i, j) ]))
        i = j
    else:
        j = i
        while j < len(content) and not isAtEmptyLine(content[j]):
            j += 1
        print toLatex(" ".join(content[i:j]))
        i = j