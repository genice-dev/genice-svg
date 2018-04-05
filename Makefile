.DELETE_ON_ERROR:
OS=$(shell uname)
ifeq ($(OS), Darwin)
	DEST=~/Library/Application\ Support/GenIce
else
	DEST=~/.genice
endif

test: CS2.svg
%.svg: formats/svg_poly.py Makefile
	genice $*     -f svg_poly > $@
prepare: #might require root privilege.
	pip install genice svgwrite
install:
	install -d $(DEST)
	install -d $(DEST)/formats
	install formats/*py $(DEST)/formats
clean:
	-rm $(ALL) *~ */*~
	-rm -rf */__pycache__
