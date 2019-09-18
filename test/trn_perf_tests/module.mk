
perftest::
ifdef nocleanup
	echo "Retaining test environment. Please delete containers after debugging"
	export NOCLEANUP=1; sudo python3 -W ignore -m unittest discover test/trn_perf_tests/ -v
else
	sudo python3 -W ignore -m unittest discover test/trn_perf_tests/ -v
endif

.PHONY: run_perf_test
run_perf_test:
ifdef nocleanup
	echo "Retaining test environment. Please delete containers after debugging"
	export NOCLEANUP=1; sudo python3 -W ignore -m unittest test.trn_perf_tests.${TEST}
else
	sudo python3 -W ignore -m unittest test.trn_perf_tests.${TEST}
endif

clean::
	rm -rf test/trn_perf_tests/__pycache__
	rm -rf test/trn_perf_tests/*.pyc
