.DELETE_ON_ERROR:
test: iceT2.svg.test CS2.svg iceR.svg CS2.png
iceT2.svg: genice_svg/formats/svg.py Makefile
	genice iceT2 -f svg[shadow] > $@
CS2.svg: genice_svg/formats/svg.py Makefile
	genice CS2 -f svg[rotatey=15:rotatex=5:polygon] > $@
iceR.svg: genice_svg/formats/svg.py Makefile
	genice iceR -f svg[rotatex=-35:rotatey=45:shadow] > $@
CS2.png: genice_svg/formats/png.py Makefile
	genice CS2 -f png[rotatey=15:rotatex=5:shadow] > $@
%.test:
	make $*
	diff $* ref/$*
check:
	./setup.py check
install:
	./setup.py install
pypi: check
	./setup.py sdist bdist_wheel upload
clean:
	-rm $(ALL) *~ */*~ *svg *png
	-rm -rf build dist *.egg-info
	-find . -name __pycache__ | xargs rm -rf
