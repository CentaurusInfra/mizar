
e2efunctest:: all
ifdef nocleanup
	echo "Retaining test environment. Please delete containers after debugging"
	export NOCLEANUP=1; sudo python3 -W ignore -m unittest discover test-e2e/ -v
else
	sudo python3 -W ignore -m unittest discover test-e2e -v
endif

.PHONY: run_e2efunc_test
run_e2efunc_test:
ifdef nocleanup
	echo "Retaining test environment. Please delete containers after debugging"
	export NOCLEANUP=1; sudo python3 -W ignore -m unittest test-e2e.${TEST}
else
	sudo python3 -W ignore -m unittest test-e2e.${TEST}
endif

clean::
	rm -rf test-e2e/__pycache__
	rm -rf test-e2e/*.pyc
