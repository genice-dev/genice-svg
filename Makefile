.DELETE_ON_ERROR:
GENICE=genice2
BASENAME=genice2_svg
PIPNAME=genice2-svg
INKSCAPE=/Applications/Inkscape.app/Contents/MacOS/inkscape

all: README.md

pep8:
		autopep8 -r -a -a -i genice2_svg/

test: iceT2.svg.test CS2.svg iceR.svg CS2.png 4R.png
iceT2.svg: $(BASENAME)/formats/svg.py Makefile
	( cd $(BASENAME) && $(GENICE) iceT2 -f svg[shadow] ) > $@
CS2.svg: $(BASENAME)/formats/svg.py Makefile
	( cd $(BASENAME) && $(GENICE) CS2 -f svg[rotate=Y15,X5:polygon] ) > $@
iceR.svg: $(BASENAME)/formats/svg.py Makefile
	( cd $(BASENAME) && $(GENICE) iceR -f svg[rotate=X-35,Y45:shadow] ) > $@
CS2.png: $(BASENAME)/formats/png.py Makefile
	( cd $(BASENAME) && $(GENICE) CS2 -f png[rotate=Y15,X5:shadow] ) > $@
4R.png: $(BASENAME)/formats/png.py Makefile
	( cd $(BASENAME) && $(GENICE) 4R -f png[shadow:rotate=X2,Y88] ) > 4R.png
%.test:
	make $*
	diff $* ref/$*
%.svg.png: %.svg
	$(INKSCAPE) -z $< -d 150 -b white -o $@

%: temp_% replacer.py $(wildcard $(BASENAME)/lattices/*.py) $(wildcard $(BASENAME)/*.py)
	pip install genice2_dev svgwrite
	python replacer.py $< > $@


test-deploy:
	poetry publish --build -r testpypi
test-install:
	pip install --index-url https://test.pypi.org/simple/ $(PIPNAME)
uninstall:
	-pip uninstall -y $(PIPNAME)
build: README.md $(wildcard genice2_yaplot/*.py)
	poetry build
deploy:
	poetry publish --build
check:
	poetry check


clean:
	-rm $(ALL) *~ */*~ *svg CS2.png
	-rm -rf build dist *.egg-info
	-find . -name __pycache__ | xargs rm -rf
