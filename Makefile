# Copyright (c) 2014
# Written by Gabriel Hjort Blindell <ghb@kth.se>

#===========
# VARIABLES
#===========

PDF_FILE := apf.pdf
APF_FILE := apf.txt
TEX_TEMPLATE_FILE := book.tex
TEX_INPUT_FILE := book-input.tex
TEX_INPUT_FILE_GEN_PY := make-tex.py
LATEX_ARGS = "\newcommand{\inputFile}{$(TEX_INPUT_FILE)} \
  \input{$(basename $(TEX_TEMPLATE_FILE))}"


#=======
# RULES
#=======

$(PDF_FILE): $(TEX_TEMPLATE_FILE) $(TEX_INPUT_FILE)
	pdflatex $(LATEX_ARGS)
	pdflatex $(LATEX_ARGS)

$(TEX_INPUT_FILE): $(APF_FILE) $(TEX_INPUT_FILE_GEN_PY)
	python $(TEX_INPUT_FILE_GEN_PY) $(APF_FILE) > $@

.PHONY: clean
clean:
	$(RM) $(TEX_INPUT_FILE)
	$(RM) *.aux *.log *.toc

.PHONY: distclean
distclean: clean
	$(RM) $(TEX_TEMPLATE_FILE).pdf
