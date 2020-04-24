mgmt_tests:: all
	sudo python3 -W ignore -m unittest discover mgmt/tests/ -v

.PHONY: run_mgmt_test
run_mgmt_test:
	sudo python3 -W ignore -m unittest mgmt.tests.${TEST} -v

clean::
	rm -rf mgmt/test/__pycache__
	rm -rf mgmt/test/*.pyc
	rm -rf mgmt/common/__pycache__
	rm -rf mgmt/common/*.pyc
