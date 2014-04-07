#!/usr/bin/python

# Copyright (c) 2014
# Written by Gabriel Hjort Blindell <ghb@kth.se>

#=========
# IMPORTS
#=========

import string
import sys
import time



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
        if string.letters.find(c) >= 0 and not string.uppercase.find(c) >= 0:
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
    sep_chars = " '\",.(-/"
    new_s = ""
    i = 0
    while i < len(s):
        start_pos = s.find(m_start, i)
        if start_pos < 0:
            break
        if start_pos + 1 < len(s) and s[start_pos + 1] == ' ':
            new_s += s[i:start_pos + 1]
            i = start_pos + 1
            continue
        must_be_within_same_word = (m_start == m_end
                                    and start_pos != 0
                                    and sep_chars.find(s[start_pos - 1]) < 0)
        end_pos = s.find(m_end, start_pos + len(m_start))
        if end_pos < 0:
            break
        do_skip = False
        if end_pos > start_pos + len(m_start):
            if s[end_pos - 1] == ' ':
                do_skip = True
                i = end_pos + len(m_end)
            if not do_skip and must_be_within_same_word:
                section_start_pos = start_pos + len(m_start)
                section = s[section_start_pos:end_pos]
                for c in sep_chars:
                    sep_pos = section.find(c)
                    if sep_pos >= 0:
                        do_skip = True
                        end_pos = section_start_pos + sep_pos
                        break
            if not do_skip:
                new_s += (s[i:start_pos]
                          + t_start
                          + s[start_pos + len(m_start):end_pos]
                          + t_end)
                i = end_pos + len(m_end)
        else:
            do_skip = True
            end_pos += len(m_end)
        if do_skip:
            new_s += s[i:end_pos]
            i = end_pos
    new_s += s[i:]
    return new_s

def toLatex(s):
    url_start = "<"
    url_end = ">"

    new_s = ""
    offset = 0
    i = offset
    while i < len(s):
        url_start_pos = s.find(url_start, i)
        if url_start_pos < 0:
            break
        is_url_start_ok = (url_start_pos + 1 < len(s)
                           and s[url_start_pos + 1] != ' ')
        if not is_url_start_ok:
            i = url_start_pos + len(url_start)
            continue
        url_end_pos = s.find(url_end, url_start_pos + len(url_start))
        if url_end_pos < 0:
            break
        is_url_end_ok = s[url_end_pos - 1] != ' '
        url_section = s[url_start_pos + len(url_start):url_end_pos]
        has_url_spaces = url_section.find(' ') >= 0
        if not is_url_end_ok or has_url_spaces:
            i = url_end_pos + len(url_end)
            continue

        # Found URL section
        new_s += (toLatexSub(s[offset:url_start_pos])
                  + "\\typesetUrl{" + url_section + "}")
        offset = url_end_pos + len(url_end)
        i = offset
    new_s += toLatexSub(s[offset:])
    return new_s

def toLatexSub(s):
    s = replace(s, "_", "_", "\\emph{", "}")
    s = replace(s, "*", "*", "\\emph{", "}")
    s = replace(s, "<<", ">>", "\\footnote{", "}")
    s = s.replace("&", "\&")
    s = s.replace("$", "\$")
    s = s.replace("%", "\%")
    s = s.replace("#", "\#")
    s = s.replace("'-'", "'\\texttt{-}'")
    s = s.replace("'+'", "'\\texttt{+}'")
    s = s.replace("...", "\\ldots{}")
    s = s.replace("-->", "$\\rightarrow$")
    # TODO: add handling of 'Tyo yur atl ho sooten gatrunen'
    s = s.replace("LaTeX", "\\LaTeX")
    s = typesetUsenet(s)
    return s

def typesetUsenet(s):
    new_s = ""
    i = 0
    while i < len(s):
        start_pos = s.find("alt.", i)
        if start_pos >= 0:
            end_pos = s.find(" ", start_pos)
            if end_pos < 0:
                end_pos = len(s) - 1
            for j in reversed(range(start_pos, end_pos)):
                if string.letters.find(s[j]) >= 0:
                    end_pos = j + 1
                    break
            new_s = (s[i:start_pos]
                     + "\\typesetUsenet{"
                     + s[start_pos:end_pos] + "}")
            i = end_pos
        else:
            break
    new_s += s[i:]
    return new_s

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
            section = s[i - 1:j + 1]
            num_uppercase = 0
            at_least_two_adjacent_uppercase = False
            previous_was_uppercase = False
            for c in section:
                if c.isalpha() and c.isupper():
                    num_uppercase += 1
                    if previous_was_uppercase:
                        at_least_two_adjacent_uppercase = True
                    previous_was_uppercase = True
                else:
                    previous_was_uppercase = False
            if num_uppercase >= 3 and at_least_two_adjacent_uppercase:
                section = section[0] + section[1:].lower()

                # Make 'I' into uppercase
                k = 0
                while k < len(section):
                    if (section[k] == 'i'
                        and (k + 1 < len(section)
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
                    if section[k] == '.' or section[k] == '?':
                        if k + 2 < len(section) and section[k + 1] == ' ':
                            section = (section[:k + 2]
                                       + section[k + 2].upper()
                                       + section[k + 3:])
                            k += 3
                        else:
                            k += 1
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

def typesetHex(s):
    new_s = ""
    plus_start_pos = s.find("+")
    if plus_start_pos >= 0:
        plus_end_pos = s.rfind("+", plus_start_pos + 1)
        if plus_end_pos >= 0:
            plus_end_pos += 1
            return (s[:plus_start_pos]
                    + "\\texttt{" + s[plus_start_pos:plus_end_pos] + "}"
                    + s[plus_end_pos])
    return s

def extractQuoteParts(s):
    pos = s.find("] ")
    if pos >= 0:
        return s[0], s[2:pos + 1], s[pos + 2:]
    else:
        pos = s.find(" ")
        if pos >= 0:
            return s[0], s[2:pos], s[pos + 1:]
        else:
            reportError("Invalid quote syntax")

def extractMetaData(content, tag):
    for i in range(len(content)):
        line = content[i]
        start_pos = line.find(tag + ":")
        if start_pos >= 0:
            # Meta data found
            data = line[line.find(":") + 1:].strip()

            # Get all data (if it continues on the next line)
            for j in range(i + 1, len(content)):
                line = content[j]
                if len(line) > 0 and line[0] == '\t':
                    data += " " + line.strip()
                else:
                    break
            return data
    # Whole document scanned without finding the tag
    reportError("Metadata tag '" + tag + "' not found")

def printMetadata(cmd_suffix, value):
    print "\\renewcommand{\\this" + cmd_suffix + "}{" + toLatex(value) + "}"

def onlyOneDot(s):
    pos = s.find(" ")
    if pos >= 0:
        s = s[0:pos]
    pos = s.find(".")
    if pos >= 0:
        pos = s.find(".", pos + 1)
        if pos >= 0:
            return s[0:pos]
    return s



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
printMetadata("Title", "The Annotated Pratchett File")
printMetadata("Subtitle", onlyOneDot(extractMetaData(content, "Version")))
printMetadata("ArchiveName", extractMetaData(content, "Archive-name"))
printMetadata("LastModified", extractMetaData(content, "Last-modified"))
printMetadata("FullVersion", extractMetaData(content, "Version"))
printMetadata("Editor", extractMetaData(content, "Editor"))
printMetadata("AssistantEditor", extractMetaData(content, "Assistant-Editor"))
printMetadata("DocUrl", extractMetaData(content, "URL"))
printMetadata("Newsgroups", extractMetaData(content, "Newsgroups"))
printMetadata("Subject", extractMetaData(content, "Subject"))
printMetadata("DocBuild", time.strftime("%Y-%m-%d %H:%M:%S"))
print

print "\\frontmatter"
print "\\makeTitlePage"
print "\\makeCopyrightPage"
print "\\makeTOCPage"
print
print "\\mainmatter"
print

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
            print ("\\item "
                   + toLatex(
                        " ".join([ content[k].strip() for k in range(i, j) ])
                     )
                   )
            i = j
        print "\end{indentText}"
    elif isAtTextExcerpt(content[i]):
        print "\\begin{excerptText}"
        while i < len(content) and isAtTextExcerpt(content[i]):
            j = i + 1
            while j < len(content) and isAtTextExcerptContinue(content[j]):
                j += 1
            print ("\\item "
                   + toLatex(
                        " ".join([ content[k].strip() for k in range(i, j) ])
                     )
                   )
            i = j
        print "\end{excerptText}"
    elif isAtQuote(content[i]):
        j = i + 1
        while j < len(content) and isAtQuoteContinue(content[j]):
            j += 1
        sign, pages, quote = extractQuoteParts(
            " ".join([ content[k].strip() for k in range(i, j) ])
            )
        print ("\\apQuote{"
               + sign
               + "}{"
               + pages.replace("p. ", "p.\\ ")
               + "}{"
               + toLatex(typesetHex(typesetDeath(quote)))
               + "}")
        i = j
    elif isAtEmptyLine(content[i]):
        print
        i += 1
    elif isAtQuoteDescription(content[i]):
        j = i + 1
        while j < len(content) and isAtQuoteDescriptionContinue(content[j]):
            j += 1
        text = toLatex(" ".join([ content[k].strip() for k in range(i, j) ]))
        if text[0].isalpha() and text[0].islower():
            print "\\noindent"
        print text
        i = j
    else:
        j = i
        while j < len(content) and not isAtEmptyLine(content[j]):
            j += 1
        text = toLatex(" ".join(content[i:j]))
        if text[0].isalpha() and text[0].islower():
            print "\\noindent"
        print text
        i = j
