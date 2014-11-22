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

def reportDebug(msg):
    sys.stderr.write(msg + "\n")

def reportError(msg):
    sys.stderr.write( "ERROR, somewhere around line "
                    + str(currentLine + 1)
                    + ":\n"
                    )
    sys.stderr.write(msg + "\n")

def reportErrorAndExit(msg):
    reportError(msg)
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
        reportErrorAndExit("Invalid chapter syntax");
    return s[4:].strip()

def isAtSectionName(s):
    if len(s) == 0 or s[0] == ' ':
        return False
    for c in s:
        if string.letters.find(c) >= 0 and not string.uppercase.find(c) >= 0:
            return False
    return True

def extractSectionName(s):
    s = s[0] + s[1:].rstrip().lower()

    # Custom fixes
    s = s.replace(" ii:", " 2:")
    s = s.replace(" iii:", " 3:")
    s = s.replace(" iv:", " 4:")
    s = s.replace(" v:", " 5:")
    s = s.replace(" apf", " APF")

    # Make every start of word uppercase
    i = 0
    while i < len(s):
        if s[i] == ' ' or s[i] == '-':
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

    # Uppercase words after certain characters
    i = 0
    while i < len(s):
        if s[i] == ':':
            i += 2
            s = s[:i] + s[i].upper() + s[i + 1:]
        else:
            i += 1

    return s

def checkSpacesExact(s, num):
    return len(s) > num + 1 and s[0:num] == (" " * num) and s[num] != ' '

def checkSpacesAtLeast(s, num):
    return len(s) > num + 1 and s[0:num] == (" " * num)

def isAtQuote(s):
    return len(s) > 2 and (s[0] == '-' or s[0] == '+') and s[1] == ' '

def isAtQuoteContinue(s):
    return checkSpacesExact(s, 2)

def isAtQuoteText(s):
    return (  isAtQuoteParagraph(s)
           or isAtQuoteIndentedText(s)
           or isAtQuoteTextExcerpt(s)
           )

def isAtQuoteParagraph(s):
    return checkSpacesExact(s, 2)

def isAtQuoteParagraphContinue(s):
    return checkSpacesExact(s, 2)

def isAtQuoteIndentedText(s):
    return checkSpacesExact(s, 6)

def isAtQuoteIndentedTextContinue(s):
    return checkSpacesAtLeast(s, 7)

def isAtQuoteTextExcerpt(s):
    return checkSpacesExact(s, 8)

def isAtQuoteTextExcerptContinue(s):
    return checkSpacesAtLeast(s, 9)

def isAtSomethingOtherThanMiscText(s):
    return (  isAtChapterSeparator(s)
           or isAtSectionName(s)
           or isAtQuote(s)
           )

def isAtMiscText(s):
    return (   not isAtSomethingOtherThanMiscText(s)
           and (  isAtMiscParagraph(s)
               or isAtMiscQuoteText(s)
               or isAtMiscIndentedText(s)
               or isAtMiscTextExcerpt(s)
               )
           )


def isAtMiscParagraph(s):
    return checkSpacesExact(s, 0) and not isAtSomethingOtherThanMiscText(s)

def isAtMiscParagraphContinue(s):
    return checkSpacesExact(s, 0)

def isAtMiscQuoteText(s):
    return checkSpacesExact(s, 2)

def isAtMiscQuoteTextContinue(s):
    return checkSpacesExact(s, 2)

def isAtMiscIndentedText(s):
    return checkSpacesExact(s, 6)

def isAtMiscIndentedTextContinue(s):
    return checkSpacesAtLeast(s, 7)

def isAtMiscTextExcerpt(s):
    return checkSpacesExact(s, 8)

def isAtMiscTextExcerptContinue(s):
    return checkSpacesAtLeast(s, 9)

def isAtEmptyLine(s):
    return len(s) == 0

def latexifyMarkup(s):
    # Element within the list:
    #    #0: String that starts markup
    #    #1: String that ends markup
    #    #2: String to replace the markup start with
    #    #3: String to replace the markup end with
    #    #4: Whether the markup can occur in the middle of a word
    #    #5: Whether the markup can span across multiple paragraphs
    r_data = [ [ "_",  "_",     "\\emph{",  "}", False, False ]
             , [ "*",  "*",     "\\emph{",  "}",  True, False ]
             , ["<<", ">>", "\\footnote{",  "}", False, False ]
             , [ "'",  "'",           "`",  "'", False, False ]
             , ["\"", "\"",          "``", "''", False,  True ]
             ]

    # Find earliest start of (any) markup
    r_index = -1
    start_pos = sys.maxint
    has_improper_start = False
    for i in range(len(r_data)):
        offset = 0
        while offset < len(s):
            search_str = r_data[i][0]
            pos, starts_before_word = findMarkupStart(s, search_str, offset)
            if pos >= 0:
                are_improper_starts_allowed = r_data[i][4]
                if starts_before_word or are_improper_starts_allowed:
                    if pos < start_pos:
                        r_index = i
                        start_pos = pos
                        has_improper_start = not starts_before_word
                    break
                else:
                    offset = pos + len(search_str)
            else:
                break
    if r_index < 0:
        # No start of markup found
        return s

    # Find end of markup (remember that markups can be nested)
    markup_start_str = r_data[r_index][0]
    markup_end_str = r_data[r_index][1]
    end_pos = -1
    level = 1
    offset = start_pos + len(markup_start_str)

    while offset < len(s):
        end_pos, stops_after_word = findMarkupStop(s, markup_end_str, offset)
        if end_pos >= 0:
            new_start_pos, new_starts_before_word = \
                findMarkupStart(s, markup_start_str, end_pos)
            stop_could_be_new_markup_start = \
                new_start_pos == end_pos and new_starts_before_word

            # If the start and end position completely wraps the start of *some*
            # markup (not necessarily) the same, then the potential start of a
            # nested markup becomes an actual start
            is_start_of_new_markup = False
            if stop_could_be_new_markup_start:
                text_between_markup = \
                    s[start_pos + len(markup_start_str):end_pos]

                for i in range(len(r_data)):
                    if text_between_markup == r_data[i][0]:
                        is_start_of_new_markup = True
                        break
            if is_start_of_new_markup:
                level += 1
                offset = end_pos + len(markup_end_str)
                continue

            if stops_after_word:
                level -= 1
            else:
                if not has_improper_start:
                    # Only proper markups (that is, markups which start at a
                    # word and end after a word) may be nested
                    if stop_could_be_new_markup_start:
                        level += 1
                    else:
                        are_improper_stops_allowed = r_data[r_index][4]
                        if are_improper_stops_allowed:
                            level -= 1
                else:
                    # All found stops are always valid if the start is improper
                    level -= 1
            if level > 0:
                offset = end_pos + len(markup_end_str)
                continue

            # Found valid markup region
            replace_start_str = r_data[r_index][2]
            replace_end_str = r_data[r_index][3]
            s_within_markup = s[start_pos + len(markup_start_str):end_pos]
            s_after_markup = s[end_pos + len(markup_end_str):]
            return ( s[:start_pos]
                   + replace_start_str
                   + latexifyMarkup(s_within_markup)
                   + replace_end_str
                   + latexifyMarkup(s_after_markup)
                   )
        else:
            # No end of markup found
            break

    # Failed to find end of markup
    reportErrorAndExit( "Required end of markup ("
                      + markup_end_str
                      + ") not found (perhaps due to incorrected nesting)"
                      )

def findMarkupStart(s, start_str, offset = 0, stop = -1):
    init_word_chars = " /-'\"*_([\n"
    if stop < 0:
        stop = len(s)

    start_pos = s.find(start_str, offset, stop)
    if start_pos == 0:
        return (start_pos, True)
    elif start_pos > 0:
        return (start_pos, init_word_chars.find(s[start_pos - 1]) >= 0)
        # The second value is a Boolean indicating whether the markup starts
        # right before a word
    else:
        # No valid markup start found
        return (-1, False)

def findMarkupStop(s, end_str, offset = 0, stop = -1):
    term_word_chars = " /-,.;:!?'\"*_)[]\n"
    if stop < 0:
        stop = len(s)

    end_pos = s.find(end_str, offset, stop)
    if end_pos > 0:
        after_markup_pos = end_pos + len(end_str)
        if after_markup_pos == len(s):
            return (end_pos, True)
        else:
            return (end_pos, term_word_chars.find(s[after_markup_pos]) >= 0)
            # The second value is a Boolean indicating whether the markup stops
            # right after a word
    else:
        # No valid markup stop found
        return (-1, False)

def toLatex(s):
    URL_START_STR = "<"
    URL_END_STR = ">"
    REPLACE_START_STR = "<["
    REPLACE_END_STR = "]>"

    urls = []
    s_wo_urls = ""
    offset = i = 0
    while i < len(s):
        # Find start and end of URL
        start_pos = s.find(URL_START_STR, i)
        if start_pos < 0:
            break
        is_url_start_ok = (   start_pos + 1 < len(s)
                          and s[start_pos + 1] != ' '
                          )
        if not is_url_start_ok:
            i = start_pos + len(URL_START_STR)
            continue
        end_pos = s.find(URL_END_STR, start_pos + len(URL_START_STR))
        if end_pos < 0:
            break

        # Check that we've actually found an URL and not something else
        url_text = s[start_pos + len(URL_START_STR):end_pos]
        is_url_end_ok = s[end_pos - 1] != ' '
        has_url_spaces = url_text.find(' ') >= 0
        if (  not is_url_end_ok
           or has_url_spaces
           or (   not url_text.find("@") >= 0
              and not url_text[:7] == "http://"
              and not url_text[:6] == "ftp://"
              )
           ):
            i = end_pos + len(URL_END_STR)
            continue

        # Replace URL with place-holder text
        url_replace_str = REPLACE_START_STR + str(len(urls)) + REPLACE_END_STR
        urls.append(url_text)
        s_wo_urls += s[offset:start_pos] + url_replace_str
        offset = i = end_pos + 1
    s_wo_urls += s[offset:]

    new_s = toLatexSub(s_wo_urls)

    # Replace place-holders with URLs
    for i in range(len(urls)):
        new_s = new_s.replace( REPLACE_START_STR + str(i) + REPLACE_END_STR
                             , "\\typesetUrl{" + urls[i] + "}"
                             )

    return new_s

def toLatexSub(s):
    # Avoid special cases that will break the markup routine
    s = s.replace(" * ", " &m& ")
    s = s.replace("'*'", "'&m&'")
    s = s.replace( "P**! P*! B****! B**! D******!"
                 , "P&m&&m&! P&m&! B&m&&m&&m&&m&! B&m&&m&! D&m&&m&&m&&m&&m&&m&!"
                 )
    s = s.replace(" 'n' ", " &q&n&q& ")
    valid_word_start_chars = "\"' _*("
    valid_word_stop_chars = " ,.!?_*\""
    words_starting_with_quote = [ "92"
                                , "Ave"
                                , "cos"
                                , "E's"
                                , "Ello"
                                , "Em"
                                , "em"
                                , "Ere"
                                , "ere"
                                , "eroes"
                                , "im"
                                , "list"
                                , "m"
                                , "n"
                                , "Nor"
                                , "ow's"
                                , "S"
                                , "s"
                                , "t"
                                , "Til"
                                , "til"
                                , "Tis"
                                , "tis"
                                , "tween"
                                , "Twas"
                                , "twere"
                                , "twixt"
                                ]
    words_ending_with_quote = [ "An"
                              , "an"
                              , "Cornwallis"
                              , "drillin"
                              , "Evenin"
                              , "goin"
                              , "hustlin"
                              , "James"
                              , "Jus"
                              , "jus"
                              , "lukin"
                              , "makin"
                              , "o"
                              , "paradin"
                              , "Roberts"
                              , "Wi"
                              , "wouldna"
                              ]
    for w in words_starting_with_quote:
        for cs in valid_word_start_chars:
            for ce in valid_word_stop_chars:
                s = s.replace(cs + "'" + w + ce, cs + "&q&" + w + ce)
    for w in words_ending_with_quote:
        for cs in valid_word_start_chars:
            for ce in valid_word_stop_chars:
                s = s.replace(cs + w + "'" + ce, cs + w + "&q&" + ce)

    s = latexifyMarkup(s)

    # Remove initial space before footnotes due to the need to have a space
    # in order to initiate the markup
    s = s.replace(" \\footnote{", "\\footnote{")

    # Undo special cases
    s = s.replace("&m&", "*")
    s = s.replace("&q&", "'")

    # Replace special characters
    s = s.replace("&", "\\&")
    s = s.replace("$", "\\$")
    s = s.replace("%", "\\%")
    s = s.replace("#", "\\#")
    s = s.replace("_", "\\_")
    s = s.replace("^", "\\^{}")
    s = s.replace("`-'", "`$-$'")
    s = s.replace("`+'", "`$+$'")
    s = s.replace(" * ", " $*$ ")
    s = s.replace("`*'", "`$*$'")
    s = s.replace("[...]", "\\bracketsLDots{}")
    s = s.replace("...", "\\ldots{}")
    s = s.replace(" -- ", " \emdash{} ")
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
    s = s.replace("<heart>", "\heartSymbol{}\label{heart-symbol}")
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

    # Typeset certain text parts as Death
    s = s.replace("\"I DON'T KNOW ABOUT YOU, BUT I COULD MURDER A CURRY\"",
                  "\"\\typesetDeath{I don't know about you, but I could murder "
                  + "a curry}\"")

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

    # Other layout fixes
    s = s.replace(" ]", "~]")
    s = s.replace(" p. ", " p.~")
    s = s.replace("(p. ", "(p.~")
    s = s.replace(" pp. ", " pp.~")
    s = s.replace("(pp. ", "(pp.~")

    # A period followed by a lowercase letter is not a full stop
    i = 0
    while i + 2 < len(s):
        pos = s.find(". ", i)
        if pos < 0:
            break
        if s[pos + 2].islower():
            s = s[:pos] + ".\\ " + s[pos + 2:]
            i = pos + 2
        else:
            i = pos + 1

    return s

def typesetUsenet(s):
    new_s = ""
    i = 0
    while i < len(s):
        start_pos = s.find("alt.", i)
        if start_pos < 0:
            start_pos = s.find("rec.", i)
        elif start_pos < 0:
            start_pos = s.find("sci.", i)
        elif start_pos < 0:
            start_pos = s.find("lspace.", i)
        if start_pos >= 0:
            end_pos = start_pos
            while (   end_pos < len(s)
                  and (  s[end_pos].isalpha()
                      or s[end_pos] == '.'
                      )
                  ):
                end_pos += 1
            if s[end_pos - 1] == '.':
                end_pos -= 1
            for j in reversed(range(start_pos, end_pos)):
                if string.letters.find(s[j]) >= 0:
                    end_pos = j + 1
                    break
            new_s += ( s[i:start_pos]
                     + "\\typesetUsenet{"
                     + s[start_pos:end_pos]
                     + "}"
                     )
            i = end_pos
        else:
            break
    new_s += s[i:]

    new_s = new_s.replace(" a.f.p. ", " \\typesetUsenet{a.f.p.} ")

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
                    has_space = (    has_next_pos
                                and s[last_pos:next_pos].find(" ") >= 0
                                )
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
            if (   num_uppercase >= 3
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
               and section != ( "HLISTEN TO ZEE CHILDREN OFF DER NIGHT... VOT "
                              + "VONDERFUL MHUSICK DEY MAKE"
                              )
               and section != "WHAT WE ARE FIGHTING FOR"
               and section != ( "NEITHER RAIN NOR SNOW NOR GLO M OF NI T CAN "
                              + "STAY THESE MES ENGERS ABO T THEIR DUTY"
                              )
               ):
                section = section[0] + section[1:].lower()

                # Make 'I' into uppercase
                k = 0
                while k < len(section):
                    if (    section[k] == 'i'
                       and (   k + 1 < len(section)
                           and not section[k + 1].isalpha()
                           )
                       and (  k == 0
                           or not section[k - 1].isalpha()
                           )
                       ):
                        section = ( section[:k]
                                  + section[k].upper()
                                  + section[k + 1:]
                                  )
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
            return ( s[:plus_start_pos]
                   + "\\texttt{"
                   + s[plus_start_pos:plus_end_pos] + "}"
                   + s[plus_end_pos]
                   )
    return s

def fixBadTypesetting(s):
    # Prevent ligatures as this makes gothic fonts harder to read
    new_s = ""
    for c in s:
        new_s += c
        if c.isalpha():
            new_s += "\\/"

    # Prevent that 's' looks like an 'f' (this happens when using gothic fonts)
    new_s = new_s.replace("s", "s:")

    return new_s

def extractQuoteParts(s):
    sign = ""
    pages = ""
    quote = ""
    pos = s.find("]")
    if s[2] == "[" and pos >= 0:
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
            reportErrorAndExit("Invalid quote syntax")

    # Some truly UGLY fixes for solving overflowing \hboxes, but I can find
    # no better way of doing it...
    quote = quote.replace("\"Whoever would be wearing those suits, "
                          + "Rincewind decided, was expecting to boldly go "
                          + "where no man [...] had boldly gone before [...]\"",
                          "\"Whoever would be wearing those suits, \\\\"
                          + "Rincewind decided, was expecting to boldly go "
                          + "where no man [...] had boldly gone before [...]\"")
    quote = quote.replace("\"[...] the only turtle ever to feature on the "
                          + "Hertzsprung-Russell Diagram, [...]\"",
                          "\"[...] the only turtle ever to feature on the \\\\"
                          + "Hertzsprung-Russell Diagram, [...]\"")
    quote = quote.replace("\"'Truly, the world is the mollusc of your "
                          + "choice...'\"",
                          "\"'Truly, the world is the mollusc of your\\\\ "
                          + "choice...'\"")
    quote = quote.replace("\"'It sounded like 'I want to be a lawn', I "
                          + "thought?'\"",
                          "\"'It sounded like 'I want to be a lawn',\\\\"
                          + "I thought?'\"")
    quote = quote.replace("\"'I think perhaps Lance-Constable Angua "
                          + "shouldn't have another go with the longbow "
                          + "until we've worked out how to stop her... "
                          + "her getting in the way.'\"",
                          "\"'I think perhaps Lance-Constable Angua \\\\"
                          + "shouldn't have another go with the longbow "
                          + "until we've worked out how to stop her... "
                          + "her getting in the way.'\"")
    quote = quote.replace("\"It read: 'HLISTEN TO ZEE CHILDREN OFF DER "
                          + "NIGHT... VOT VONDERFUL MHUSICK DEY MAKE. "
                          + "Mnftrd. by Bergholt Stuttley Johnson, "
                          + "Ankh-Morpork.' 'It's a Johnson,' she "
                          + "breathed. 'I haven't got my hands on a Johnson "
                          + "for ages...'\"",
                          "\"It read: 'HLISTEN TO ZEE CHILDREN OFF DER "
                          + "NIGHT... VOT VONDERFUL MHUSICK DEY MAKE. "
                          + "Mnftrd. by Bergholt Stuttley Johnson, "
                          + "Ankh-\\\\Morpork.' 'It's a Johnson,' she "
                          + "breathed. 'I haven't got my hands on a Johnson "
                          + "for ages...'\"")

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
    reportErrorAndExit("Metadata tag '" + tag + "' not found")

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
    return s[0].isalpha() and s[0].islower()

def isUrlPar(s):
    return len(s) > 12 and s[:12] == "\\typesetUrl{" and s[-1] == '}'

def printParagraph(s):
    if isContinuePar(s) or isUrlPar(s):
        print "\\noindent%"
    if isUrlPar(s):
        print "\\RaggedRight%"
    print s
    if isUrlPar(s):
        print "\\par\\justifying%"

def toSingleLine(lines):
    return " ".join([ lines[k].strip() for k in range(len(lines)) ])



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
printMetadata("Summary", extractMetaData(content, "Summary"))
printMetadata("DocBuild", time.strftime("%Y-%m-%d %H:%M:%S"))
print

print "\\frontmatter"
print "\\makeTitlePage"
print "\\makeCopyrightPage"
print "\\makePreamblePage"
print "\\makeTOCPage"
print

# Move to beginning of first chapter
currentLine = 0
while True:
    line = content[currentLine]
    if isAtChapterSeparator(line):
        break
    currentLine += 1
    if currentLine >= len(content):
        reportErrorAndExit("Beginning of first chapter not found")

# Process regular content
isFirstChapter = True
hasPrintedMainMatterCommand = False
isAtVersionSection = False
isAfterAPQuote = False
while currentLine < len(content):
    if isAtChapterSeparator(content[currentLine]):
        isAfterAPQuote = False
        currentLine += 1
        if isAtChapterName(content[currentLine]):
            if isFirstChapter:
                isFirstChapter = False
            else:
                if not hasPrintedMainMatterCommand:
                    hasPrintedMainMatterCommand = True
                    print "\\mainmatter"
                    print
            print ( "\\chapter{"
                  + toLatex(extractChapterName(content[currentLine]))
                  + "}"
                  )
            currentLine += 1
            if not isAtChapterSeparator(content[currentLine]):
                reportErrorAndExit("Expected chapter separator not found")
            currentLine += 1
        else:
            # At end of content
            break
    elif isAtSectionName(content[currentLine]):
        isAfterAPQuote = False
        section_name = extractSectionName(content[currentLine])
        if section_name == "Version History and Timeline":
            isAtVersionSection = True
        else:
            isAtVersionSection = False
        formatted_section_name = toLatex(section_name)
        print ( "\\section[" + formatted_section_name + "]{"
              + fixBadTypesetting(formatted_section_name)
              + "}"
              )
        currentLine += 1
    elif isAtQuote(content[currentLine]):
        isAfterAPQuote = True
        j = currentLine + 1
        while j < len(content) and isAtQuoteContinue(content[j]):
            j += 1
        sign, pages, quote = \
            extractQuoteParts(toSingleLine(content[currentLine:j]))
        print ( "\\apQuote{"
              + sign
              + "}{"
              + pages.replace("p. ", "p.\\:")
              + "}{"
              + toLatex(typesetHex(typesetDeath(quote)))
              + "}"
              )
        currentLine = j
    elif isAtEmptyLine(content[currentLine]):
        if isAfterAPQuote:
            print "%"
        else:
            print
        currentLine += 1
    elif isAtQuoteText(content[currentLine]) and isAfterAPQuote:
        isAfterAPQuote = False

        # All text regions will be separated by a double line break, and
        # each item within a region will be separated by a single line break.
        # The different text regions will be signified using indentation, and
        # it can be assumed that all items have exactly the same indentation
        # within a single region
        NUM_INDENTS_PARAGRAPH = 0
        NUM_INDENTS_INDENTED  = 2
        NUM_INDENTS_EXCERPT   = 4
        text = ""
        f_data = [ [ isAtQuoteParagraph
                   , isAtQuoteParagraphContinue
                   , NUM_INDENTS_PARAGRAPH
                   ]
                 , [ isAtQuoteIndentedText
                   , isAtQuoteIndentedTextContinue
                   , NUM_INDENTS_INDENTED
                   ]
                 , [ isAtQuoteTextExcerpt
                   , isAtQuoteTextExcerptContinue
                   , NUM_INDENTS_EXCERPT
                   ]
                 ]
        while (   currentLine < len(content)
              and isAtQuoteText(content[currentLine])
              ):
            for fCheck, fCheckContinue, NUM_INDENTS in f_data:
                if fCheck(content[currentLine]):
                    while (   currentLine < len(content)
                          and fCheck(content[currentLine])
                          ):
                        j = currentLine + 1
                        while (   j < len(content)
                              and fCheckContinue(content[j])
                              ):
                            j += 1
                        t = toSingleLine(content[currentLine:j])
                        text += (" " * NUM_INDENTS) + t + "\n"
                        currentLine = j
                    text += "\n"
                    break
            # Skip empty lines
            while (   currentLine < len(content)
                  and isAtEmptyLine(content[currentLine])
                  ):
                currentLine += 1
        text = toLatex(text)
        regions = text.rstrip().split("\n\n")
        is_first_region = True
        for r in regions:
            if is_first_region:
                is_first_region = False
            else:
                print

            lines = r.split("\n")
            first_line = lines[0]
            if checkSpacesExact(first_line, NUM_INDENTS_PARAGRAPH):
                # A paragraph always only contains a single line within the
                # region
                printParagraph(first_line)
            elif checkSpacesExact(first_line, NUM_INDENTS_INDENTED):
                print "\\begin{indentText}"
                for l in lines:
                    print "\\item " + l.lstrip()
                print "\end{indentText}"
            elif checkSpacesExact(first_line, NUM_INDENTS_EXCERPT):
                print "\\begin{excerptText}"
                for l in lines:
                    print "\\item " + l.lstrip()
                print "\end{excerptText}"
            else:
                reportErrorAndExit( "Unrecognized region. "
                                  + "Something is seriously wrong..."
                                  )
        print
    elif isAtMiscText(content[currentLine]):
        isAfterAPQuote = False

        # All text regions will be separated by a double line break, and
        # each item within a region will be separated by a single line break.
        # The different text regions will be signified using indentation, and
        # it can be assumed that all items have exactly the same indentation
        # within a single region
        NUM_INDENTS_PARAGRAPH = 0
        NUM_INDENTS_QUOTE     = 2
        NUM_INDENTS_INDENTED  = 4
        NUM_INDENTS_EXCERPT   = 6
        text = ""
        f_data = [ [ isAtMiscParagraph
                   , isAtMiscParagraphContinue
                   , NUM_INDENTS_PARAGRAPH
                   ]
                 , [ isAtMiscQuoteText
                   , isAtMiscQuoteTextContinue
                   , NUM_INDENTS_QUOTE
                   ]
                 , [ isAtMiscIndentedText
                   , isAtMiscIndentedTextContinue
                   , NUM_INDENTS_INDENTED
                   ]
                 , [ isAtMiscTextExcerpt
                   , isAtMiscTextExcerptContinue
                   , NUM_INDENTS_EXCERPT
                   ]
                 ]
        while (   currentLine < len(content)
              and isAtMiscText(content[currentLine])
              ):
            for fCheck, fCheckContinue, NUM_INDENTS in f_data:
                if fCheck(content[currentLine]):
                    while (   currentLine < len(content)
                          and fCheck(content[currentLine])
                          ):
                        j = currentLine + 1
                        while (   j < len(content)
                              and fCheckContinue(content[j])
                              ):
                            j += 1
                        t = toSingleLine(content[currentLine:j])
                        text += (" " * NUM_INDENTS) + t + "\n"
                        currentLine = j
                    text += "\n"
                    break
            # Skip empty lines
            while (   currentLine < len(content)
                  and isAtEmptyLine(content[currentLine])
                  ):
                currentLine += 1

        text = toLatex(text)
        regions = text.rstrip().split("\n\n")
        is_first_region = True
        for r in regions:
            if is_first_region:
                is_first_region = False
            else:
                print

            lines = r.split("\n")
            first_line = lines[0]
            if checkSpacesExact(first_line, NUM_INDENTS_PARAGRAPH):
                # A paragraph always only contains a single line within the
                # region
                if isAtVersionSection:
                    print "\\noindent%"
                printParagraph(first_line)
            elif checkSpacesExact(first_line, NUM_INDENTS_QUOTE):
                # A quote always only contains a single line within the region
                printParagraph(first_line)
            elif checkSpacesExact(first_line, NUM_INDENTS_INDENTED):
                print "\\begin{indentText}"
                for l in lines:
                    print "\\item " + l.lstrip()
                print "\end{indentText}"
            elif checkSpacesExact(first_line, NUM_INDENTS_EXCERPT):
                print "\\begin{excerptText}"
                for l in lines:
                    print "\\item " + l.lstrip()
                print "\end{excerptText}"
            else:
                reportErrorAndExit( "Unrecognized region. "
                                  + "Something is seriously wrong..."
                                  )
        print
    else:
        reportErrorAndExit("Unrecognized text region")
