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
    s = s[0] + s[1:].strip().lower()

    s = s.replace(" apf", " APF")

    # Make every start of word uppercase
    i = 0
    while i < len(s):
        if s[i] == ' ':
            i += 1
            s = s[:i] + s[i].upper() + s[i + 1:]
        else:
            i += 1

    # Make certain word lowercase
    s = s.replace(" A ", " a ")
    s = s.replace(" An ", " an ")
    s = s.replace(" And ", " and ")
    s = s.replace(" As ", " as ")
    s = s.replace(" At ", " at ")
    s = s.replace(" But ", " but ")
    s = s.replace(" By ", " by ")
    s = s.replace(" For ", " for ")
    s = s.replace(" From ", " from ")
    s = s.replace(" In ", " in ")
    s = s.replace(" Into ", " into ")
    s = s.replace(" Like ", " like ")
    s = s.replace(" Nor ", " nor ")
    s = s.replace(" Of ", " of ")
    s = s.replace(" On ", " on ")
    s = s.replace(" Onto ", " onto ")
    s = s.replace(" Or ", " or ")
    s = s.replace(" Over ", " over ")
    s = s.replace(" Per ", " per ")
    s = s.replace(" So ", " so ")
    s = s.replace(" The ", " the ")
    s = s.replace(" To ", " to ")
    s = s.replace(" Unlike ", " unlike ")
    s = s.replace(" Until ", " until ")
    s = s.replace(" Via ", " via ")
    s = s.replace(" Vs ", " vs ")
    s = s.replace(" Vs. ", " vs. ")
    s = s.replace(" With ", " with ")
    s = s.replace(" Within ", " within ")
    s = s.replace(" Without ", " without ")

    return s

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
        if (not is_url_end_ok
            or has_url_spaces
            or (not url_section.find("@") >= 0
                and not url_section[:7] == "http://"
                and not url_section[:6] == "ftp://"
                )
            ):
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
    s = replace(s, " <<", ">>", "\\footnote{", "}")
    s = replace(s, "<<", ">>", "\\footnote{", "}") # Just in case...

    s = s.replace("&", "\&")
    s = s.replace("$", "\$")
    s = s.replace("%", "\%")
    s = s.replace("#", "\#")
    s = s.replace("'-'", "'\\texttt{-}'")
    s = s.replace("'+'", "'\\texttt{+}'")
    s = s.replace("...", "\\ldots{}")
    s = s.replace(" -- ", " \!---\! ")
    s = s.replace("-->", "$\\rightarrow$")
    s = s.replace("e.g. ", "e.g.\ ")
    s = s.replace("i.e. ", "i.e.\ ")
    s = s.replace("etc. ", "etc.\ ")
    s = s.replace("LaTeX", "\\LaTeX{}")
    s = s.replace("'? Tyo yur atl ho sooten gatrunen?'",
                  "'? Ty\\o{} yur \\aa{}tl h\\o{} sooten g\\aa{}trunen?'")
    s = s.replace("doppelgaenger", "doppelg\\\"{a}nger")
    s = s.replace("Danae", "Dana\\\"{e}")
    s = s.replace("Goetterdaemmerung", "G\\\"{o}tterd\"{a}mmerung")
    s = s.replace("Bjorn Ulvaeus", "Bj\\\"{o}rn Ulvaeus")
    s = s.replace("Haendel", "H\\\"{a}ndel")
    s = s.replace("cliche", "clich\\'{e}")
    s = s.replace("Goedel", "G\\\"{o}del")
    s = s.replace("Schroedinger", "Schr\\\"{o}dinger")
    s = s.replace("Quetzovercoatl", "Quetzoverc\\'{o}atl")
    s = s.replace("flambe", "flamb\\'{e}")
    s = s.replace("Ole!", "!`Ol\\'{e}!")
    s = s.replace("Eminence", "\\'{E}minence")
    s = s.replace("Cafe", "Caf\\'{e}")
    s = s.replace("<heart>", "$\heartsuit$")
    s = s.replace("Walkuere", "Walk\\\"{u}re")
    s = s.replace("Schueschien", "Sch\\\"{u}schien")
    s = s.replace("Pluen", "Pl\\\"{u}n")
    s = s.replace("Tomas", "Tom\\'{a}s")
    s = s.replace("Nuernberg", "N\\\"{u}rnberg")
    s = s.replace("Blue Oyster", "Blue \\\"{O}yster")
    s = s.replace("(TM)", "\\texttrademark{}")
    s = s.replace("naive", "na\\\"{i}ve")
    s = s.replace("Tir-far-Thionn", "Tir-far-Thi\\'{o}nn")
    s = s.replace("Tir-fa-Tonn", "T\\'{i}r-fa-Tonn")

    s = typesetUsenet(s)
    s = typesetPath(s)
    s = s.replace(" discworld-constellations ",
                  " \\typesetPath{discworld-constellations} ")

    # Set appropriate dash for ranges
    i = 0
    while i < len(s):
        pos = s.find("-", i)
        if pos < 0:
            break
        if s[pos - 1].isdigit() and s[pos + 1].isdigit():
            s = s[:pos] + "--" + s[pos + 1:]
            i = pos + 2
        else:
            i = pos + 1

    # For fixing overflowing \hboxes
    s = s.replace("Shub-Niggurath", "Shub\hyp{}Niggurath")
    s = s.replace("Arch-Generalissimo-Father-of-His-Countryship",
                  "Arch\hyp{}Generalissimo\hyp{}Father\hyp{}of\hyp{}"
                  + "His\hyp{}Countryship")
    s = s.replace("computer-generated", "computer\hyp{}generated")
    s = s.replace("y'knowwhatI'msayin?", "y'know\-what\-I'm\-sayin?")

    return s

def typesetUsenet(s):
    new_s = ""
    i = 0
    while i < len(s):
        start_pos = s.find("alt.", i)
        if start_pos < 0:
            start_pos = s.find("rec.", i)
        if start_pos < 0:
            start_pos = s.find("sci.", i)
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

def typesetPath(s):
    new_s = ""
    i = 0
    while i < len(s):
        start_pos = s.find("/", i)
        if start_pos >= 0 and (start_pos == 0 or s[start_pos - 1] == ' '):
            next_pos = s.find("/", start_pos + 1)
            has_next_pos = next_pos >= 0
            has_space = has_next_pos and s[start_pos:next_pos].find(" ") >= 0
            if has_next_pos and not has_space:
                # Found a path
                last_pos = next_pos + 1
                # Find last slash in path
                while True:
                    next_pos = s.find("/", last_pos)
                    has_next_pos = next_pos >= 0
                    has_space = (has_next_pos
                                 and s[last_pos:next_pos].find(" ") >= 0)
                    if has_next_pos and not has_space:
                        last_pos = next_pos + 1
                    else:
                        break
                # Find end of path
                end_pos = s.find(" ", last_pos)
                if end_pos < 0:
                    end_pos = len(s)
                while not s[end_pos - 1].isalpha():
                    end_pos -= 1
                # Typeset
                new_s = (s[i:start_pos]
                         + "\\typesetPath{"
                         + s[start_pos:end_pos] + "}")
                i = end_pos
            elif has_next_pos:
                i = next_pos
            else:
                break
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
                is_end_of_smallcaps = s[k].isalpha() and not s[k].isupper()
                k += 1
                if is_end_of_smallcaps:
                    break
            if not s[j - 1].isalpha():
                j -= 1
                while not s[j].isalpha():
                    j -= 1
            section = s[i - 1:j + 1]
            num_uppercase = 0
            at_least_two_adjacent_uppercase = False
            at_least_one_space = section.find(" ") >= 0
            previous_was_uppercase = False
            for c in section:
                if c.isalpha() and c.isupper():
                    num_uppercase += 1
                    if previous_was_uppercase:
                        at_least_two_adjacent_uppercase = True
                    previous_was_uppercase = True
                else:
                    previous_was_uppercase = False
            if (num_uppercase >= 3
                and at_least_two_adjacent_uppercase
                and at_least_one_space
                and section != "VIA CLOACA"
                and section != "VENI VIDI VICI: A"
                and section != "SEE ALSO"
                and section != "LIVE FATS DIE YO GNU"
                and section != "BORN TO RUNE"
                and section != "JOE'S LIVERY STABLE"
                and section != "TINKLE. TINKLE. *FIZZ"
                and section != "TALK THAT TALK"
                and section != ("HLISTEN TO ZEE CHILDREN OFF DER NIGHT... VOT "
                                + "VONDERFUL MHUSICK DEY MAKE")
                and section != "WHAT WE ARE FIGHTING FOR"
                ):
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

                # Capitalize certain words
                section = section.replace("death", "Death")
                section = section.replace("psephopololis", "Psephopololis")

                new_s += s[offset:i - 1] + "\\typesetDeath{" + section + "}"
            else:
                new_s += s[offset:j + 1]
            offset = j + 1
            i = offset
    new_s += s[offset:]
    return new_s

def typesetHex(s):
    new_s = ""
    plus_start_pos = s.find("++")
    if plus_start_pos >= 0:
        plus_end_pos = s.rfind("+", plus_start_pos + 1)
        if plus_end_pos >= 0:
            plus_end_pos += 1
            return (s[:plus_start_pos]
                    + "\\texttt{"
                    + s[plus_start_pos:plus_end_pos] + "}"
                    + s[plus_end_pos])
    return s

def extractQuoteParts(s):
    sign = ""
    pages = ""
    quote = ""
    pos = s.find("] ")
    if pos >= 0:
        sign = s[0]
        pages = s[2:pos + 1]
        quote = s[pos + 2:].strip()
    else:
        pos = s.find(" ")
        if pos >= 0:
            sign = s[0]
            pages = s[2:pos]
            quote = s[pos + 1:].strip()
        else:
            reportError("Invalid quote syntax")

    # Fix cases which will cause overflowing \hboxes
    quote = quote.replace("DM(Unseen)", "DM(Un\\-seen)")
    quote = quote.replace("Hertzsprung-Russell", "Hertzsprung\hyp{}Russell")

    # Same but truly UGLY fixes, but I can find no better way of doing it...
    quote = quote.replace("\"'Truly, the world is the mollusc of your "
                          + "choice...'\"",
                          "\"'Truly, the world is the mollusc of your\\\\ "
                          + "choice...'\"")
    quote = quote.replace("\"'A song about Great Fiery Balls. [...] Couldn't "
                          + "really make out the words, the reason bein', the "
                          + "piano exploded.'\"",
                          "\"'A song about Great Fiery Balls. [...]\\\\ "
                          + "Couldn't really make out the words, the reason "
                          + "bein', the piano exploded.'\"")
    quote = quote.replace("\"Then it wrote: +++ Good Evening, Archchancellor. "
                          + "I Am Fully Recovered And Enthusiastic About My "
                          + "Tasks +++\"",
                          "\"Then it wrote: +++ Good Evening, "
                          + "Arch-\\\\chancellor. "
                          + "I Am Fully Recovered And Enthusiastic About My "
                          + "Tasks +++\"")
    quote = quote.replace("\"+++ Yes. I Am Preparing An Area Of Write-Only "
                          + "Memory +++\"",
                          "\"+++ Yes. I Am Preparing An Area Of Write-\\\\Only "
                          + "Memory +++\"")

    return sign, pages, quote


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

def isContinuePar(s):
    return text[0].isalpha() and text[0].islower()

def isUrlPar(s):
    return len(text) > 12 and text[:12] == "\\typesetUrl{" and text[-1] == '}'

def printParagraph(text):
    if isContinuePar(text) or isUrlPar(text):
        print "\\noindent%"
    if isUrlPar(text):
        print "\\RaggedRight%"
    print text
    if isUrlPar(text):
        print "\\par\\justifying%"



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
afterAPQuote = False
while i < len(content):
    if isAtChapterSeparator(content[i]):
        afterAPQuote = False
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
        afterAPQuote = False
        print "\\section{" + toLatex(extractSectionName(content[i])) + "}"
        i += 1
    elif isAtIndentedText(content[i]):
        afterAPQuote = False
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
        afterAPQuote = False
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
        afterAPQuote = True
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
        if afterAPQuote:
            print "%"
        else:
            print
        i += 1
    elif isAtQuoteDescription(content[i]):
        afterAPQuote = False
        j = i + 1
        while j < len(content) and isAtQuoteDescriptionContinue(content[j]):
            j += 1
        text = toLatex(" ".join([ content[k].strip() for k in range(i, j) ]))
        printParagraph(text)
        i = j
    else:
        afterAPQuote = False
        j = i
        while j < len(content) and not isAtEmptyLine(content[j]):
            j += 1
        text = toLatex(" ".join(content[i:j]))
        printParagraph(text)
        i = j
