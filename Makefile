.DELETE_ON_ERROR:
test: T2.svg CS1.svg
T2.svg: genice_svg/formats/svg.py Makefile
	genice T2 -f svg > $@
CS1.svg: genice_svg/formats/svg_poly.py Makefile
	genice CS1 -f svg_poly > $@
install:
	./setup.py install
clean:
	-rm $(ALL) *~ */*~ *svg
	-rm -rf build dist *.egg-info
	-find . -name __pycache__ | xargs rm -rf
