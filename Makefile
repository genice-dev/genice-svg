.DELETE_ON_ERROR:
test: T2.svg CS2.svg
T2.svg: genice_svg/formats/svg.py Makefile
	genice T2 -f svg[rotatey=15:rotatex=5:shadow] > $@
CS2.svg: genice_svg/formats/svg.py Makefile
	genice CS2 -f svg[rotatey=15:rotatex=5:polygon] > $@
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
