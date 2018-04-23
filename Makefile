.DELETE_ON_ERROR:
test: CS2.svg
%.svg: formats/svg_poly.py Makefile
	genice $*     -f svg_poly > $@
install:
	./setup.py install
clean:
	-rm $(ALL) *~ */*~ *svg
	-rm -rf build dist *.egg-info
	-find . -name __pycache__ | xargs rm -rf

