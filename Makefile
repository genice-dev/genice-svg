.DELETE_ON_ERROR:

all: README.md

%: temp_% replacer.py genice_svg/__init__.py genice_svg/formats/svg.py genice_svg/formats/png.py
	python replacer.py < $< > $@

test: iceT2.svg.test CS2.svg iceR.svg CS2.png 4R.png
iceT2.svg: genice_svg/formats/svg.py Makefile
	genice iceT2 -f svg[shadow] > $@
CS2.svg: genice_svg/formats/svg.py Makefile
	genice CS2 -f svg[rotatey=15:rotatex=5:polygon] > $@
iceR.svg: genice_svg/formats/svg.py Makefile
	genice iceR -f svg[rotatex=-35:rotatey=45:shadow] > $@
CS2.png: genice_svg/formats/png.py Makefile
	genice CS2 -f png[rotatey=15:rotatex=5:shadow] > $@
4R.png: genice_svg/formats/png.py Makefile
	genice 4R -f png[shadow:rotatex=2:rotatey=88] > 4R.png
%.test:
	make $*
	diff $* ref/$*


test-deploy: build
	twine upload -r pypitest dist/*
test-install:
	pip install pillow
	pip install --index-url https://test.pypi.org/simple/ genice_svg



install:
	./setup.py install
uninstall:
	-pip uninstall -y genice-svg
build: README.md $(wildcard genice_svg/formats*.py)
	./setup.py sdist bdist_wheel


deploy: build
	twine upload dist/*
check:
	./setup.py check
clean:
	-rm $(ALL) *~ */*~ *svg CS2.png
	-rm -rf build dist *.egg-info
	-find . -name __pycache__ | xargs rm -rf
