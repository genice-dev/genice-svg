.DELETE_ON_ERROR:
test: CS2.svg
%.svg: formats/svg_poly.py Makefile
	genice $*     -f svg_poly > $@
install:
	./setup.py install
clean:
	-rm $(ALL) *~ */*~ *svg
	-rm -rf __pycache__ build dist *.egg-info
