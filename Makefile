.DELETE_ON_ERROR:
test: T2.svg CS1.svg
T2.svg: genice_svg/formats/svg.py Makefile
	genice T2 -f svg > $@
CS1.svg: genice_svg/formats/svg_poly.py Makefile
	genice CS1 -f svg_poly > $@
check:
	./setup.py check
install:
	./setup.py install
pypi: check
	./setup.py sdist bdist_wheel upload
clean:
	-rm $(ALL) *~ */*~ *svg
	-rm -rf build dist *.egg-info
	-find . -name __pycache__ | xargs rm -rf
