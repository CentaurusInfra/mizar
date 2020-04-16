
e2efunctest:: all
ifdef nocleanup
	echo "Retaining test environment. Please delete containers after debugging"
	export NOCLEANUP=1; sudo python3 -W ignore -m unittest discover teste2e/ -v
else
	sudo python3 -W ignore -m unittest discover teste2e -v
endif

.PHONY: run_e2efunc_test
run_e2efunc_test:
ifdef nocleanup
	echo "Retaining test environment. Please delete containers after debugging"
	export NOCLEANUP=1; sudo python3 -W ignore -m unittest teste2e.${TEST}
else
	sudo python3 -W ignore -m unittest teste2e.${TEST} -v
endif

clean::
	rm -rf teste2e/__pycache__
	rm -rf teste2e/*.pyc
