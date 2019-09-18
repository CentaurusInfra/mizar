
functest::
ifdef nocleanup
	echo "Retaining test environment. Please delete containers after debugging"
	export NOCLEANUP=1; sudo python3 -W ignore -m unittest discover test/trn_func_tests/ -v
else
	sudo python3 -W ignore -m unittest discover test/trn_func_tests/ -v
endif

.PHONY: run_func_test
run_func_test:
ifdef nocleanup
	echo "Retaining test environment. Please delete containers after debugging"
	export NOCLEANUP=1; sudo python3 -W ignore -m unittest test.trn_func_tests.${TEST}
else
	sudo python3 -W ignore -m unittest test.trn_func_tests.${TEST}
endif

clean::
	rm -rf test/trn_func_tests/__pycache__
	rm -rf test/trn_func_tests/*.pyc
