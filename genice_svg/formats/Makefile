02075.pov: yamazaki-pov.py
	python3 ./yamazaki-pov.py < ~/Google\ Drive/02075.mdv > 02075.pov
%.sq0.png: %.pov default.inc
	povray +w500 +h500 +FN +SP32  +Q9    +A0.3 +AM2   +D -Lbin -L/usr/local/share/povray-3.7/include +HIdefault.inc -i$*.pov -O$@ #1> /dev/null 2> /dev/null
%.v1.sq0.png: %.pov v1.inc
	povray +w500 +h500 +FN +SP32  +Q9    +A0.3 +AM2   +D -Lbin -L/usr/local/share/povray-3.7/include +HIv1.inc -i$*.pov -O$@ #1> /dev/null 2> /dev/null
