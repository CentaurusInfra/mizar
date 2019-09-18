# SPDX-License-Identifier: GPL-2.0-or-later

module := test

.PHONY:
run_unittests: unittest
	echo running unittest
	find ./build/tests/ -type f -name "test_*" -exec {} \;

submodules := trn_func_tests
submodules += trn_perf_tests
-include $(patsubst %, $(module)/%/module.mk, $(submodules))
