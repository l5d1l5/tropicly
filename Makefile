# Makefile

# author: Tobias Seydewitz
# date: 24.04.19
# mail: seydewitz@pik-potsdam.de
# institution: Potsdam Institute for Climate Impact Research

.PHONY: help install download mask interalgin intersection alignment aism

## Instal Python requirements to "/home/username/.local/lib/python3.*/site-packages".
install:
	pip3 install -r requirements.txt


### PIPELINE

# rule options: [gfc, agb, soc, ifl, auxiliary, all] [integer]
## Download the required strata, includes GFC, IFL, AGB, GSOCmap, and NaturalEarth.
## The GL30 strata (2000 and 2010) must be added to the folder "/data/raw/gl30" manually.
download:
	python3 tropicly/download.py all 4

# rule options: [gfc, gl30, agb, soc, aism, all]
## Create strata masks for GFC, GL30, AGB, and GSOCmap strata.
## Theses masks are fundmental for the alignment process.
mask:
	python3 tropicly/masking.py gfc
	python3 tropicly/masking.py gl30
	python3 tropicly/masking.py agb
	python3 tropicly/masking.py soc

# rule options: [intersect, align, clean] [integer]
## Create strata intersection layer from masks, perform strata alignment with intersection layer,
## delete temporary files, and create a mask of the aligned strata.
interalgin:
	python3 tropicly/alignment.py intersect 8
	python3 tropicly/alignment.py align 8
	python3 tropicly/alignment.py clean 8
	python3 tropicly/masking.py aism

# rule options: [str] [integer]
## Create data for developing the forest definition by computing the jaccard index for GL30_2000 and
## GFC treecover2000 with varying canopy densities.
definition:
	python3 tropicly/definition.py fordef.csv 8


### ATOMIC PIPELINE STEPS

intersection:
	python3 tropicly/alignment.py intersect 1

alignment:
	python3 tropicly/alignment.py align 8

aism:
	python3 tropicly/masking.py aism

# Taken from cookiecutter data-science template
# Inspired by <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
# sed script explained:
# /^##/:
# 	* save line in hold space
# 	* purge line
# 	* Loop:
# 		* append newline + line to hold space
# 		* go to next line
# 		* if line starts with doc comment, strip comment character off and loop
# 	* remove target prerequisites
# 	* append hold space (+ newline) to line
# 	* replace newline plus comments by `---`
# 	* print line
# Separate expressions are necessary because labels cannot be delimited by
# semicolon; see <http://stackoverflow.com/a/11799865/1968>
help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@echo
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')