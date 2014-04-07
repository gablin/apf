# Copyright (c) 2014
# Written by Gabriel Hjort Blindell <ghb@kth.se>

#===========
# VARIABLES
#===========

PDF_FILE := apf.pdf
APF_FILE := apf.txt
TEX_TEMPLATE_FILE := book.tex
TEX_INPUT_FILE := book-input.tex



#=======
# RULES
#=======

$(PDF_FILE): $(TEX_TEMPLATE_FILE) $(TEX_INPUT_FILE)
	pdflatex $(basename $(TEX_TEMPLATE_FILE))
	pdflatex $(basename $(TEX_TEMPLATE_FILE))

$(TEX_INPUT_FILE): $(APF_FILE)
	python make-tex.py $(APF_FILE) > $@

.PHONY: clean
clean:
	$(RM) $(TEX_TEMPLATE_FILE)

.PHONY: distclean
distclean: clean
	$(RM) $(TEX_INPUT_FILE)
