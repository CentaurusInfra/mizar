# SPDX-License-Identifier: GPL-2.0-or-later

modules := src test
build := build

CC = gcc
ARCH := $(shell uname -m)

# Sanitizer
SANITIZE.x86_64 += -mmpx
SANITIZE.aarch64 :=

SANITIZE += $(SANITIZE.$(ARCH))

SANITIZE += -fsanitize=leak
SANITIZE += -fsanitize=undefined

SANITIZE += -fsanitize=shift
SANITIZE += -fsanitize=integer-divide-by-zero
SANITIZE += -fsanitize=unreachable
SANITIZE += -fsanitize=vla-bound
SANITIZE += -fsanitize=null
SANITIZE += -fsanitize=return
SANITIZE += -fsanitize=signed-integer-overflow
SANITIZE += -fsanitize=bounds
SANITIZE += -fsanitize=alignment
SANITIZE += -fsanitize=object-size
SANITIZE += -fsanitize=float-divide-by-zero
SANITIZE += -fsanitize=float-cast-overflow
SANITIZE += -fsanitize=nonnull-attribute
SANITIZE += -fsanitize=returns-nonnull-attribute
SANITIZE += -fsanitize=bool
SANITIZE += -fsanitize=enum
SANITIZE += -fsanitize=vptr

SANITIZE += -fno-omit-frame-pointer

## CFLAGS
CFLAGS += -I.
CFLAGS += -Ilib/usr/include
CFLAGS += -g -O3 -DDEBUG -Llib
CFLAGS += -std=c11
CFLAGS += -D_POSIX_C_SOURCE
CFLAGS += -Wall
CFLAGS += -Wextra
CFLAGS += -Werror
CFLAGS += -pedantic -Wpedantic

CFLAGS += -fno-common
CFLAGS += -fstrict-aliasing

CFLAGS += $(SANITIZE)

## LDFLAGS
LDFLAGS.x86_64 += -Llib/usr/lib64
LDFLAGS.aarch64 += -Llib/usr/lib

LDFLAGS += $(LDFLAGS.$(ARCH))
LDFLAGS += -l:libbpf.a
LDFLAGS += -l:libelf.a
LDFLAGS += -lz
LDFLAGS += -lnsl
LDFLAGS += -static-liblsan
LDFLAGS += -static-libubsan
$(info LDFLAGS=$(LDFLAGS))

LLC=llc-7 -march=bpf -filetype=obj
CLANG=clang-7
CLANGFLAGS= -I.\
			-Wno-unused-value -Wno-pointer-sign\
			-Wno-compare-distinct-pointer-types \
			-Wno-gnu-variable-sized-type-not-at-end \
			-Wno-address-of-packed-member -Wno-tautological-compare \
			-Wno-unknown-warning-option -O3 -emit-llvm -c -o -

CLANGFLAGS_DEBUG:= -DDEBUG -D__KERNEL__ -g -D__BPF_TRACING__ $(CLANGFLAGS)

#all:  rpcgen transit transitd xdp
all:: dirmake libbpf

-include $(patsubst %, %/module.mk, $(modules))

.PHONY: clean
clean::
	rm -f cov/*
	rm -rf lcov/*
	rm -rf build/bin/*
	rm -rf build/tests/*
	rm -f *.gcov

.PHONY: test
test:: lcov functest

.PHONY: unittest
unittest::

.PHONY:
gcov: run_unittests
	GCOV_PREFIX=cov; gcov $(clisrc)
	GCOV_PREFIX=cov; gcov $(dmnsrc)

.PHONY: lcov
lcov:gcov
	lcov -d . -b . -c -o lcov/transit_cov.info
	lcov --remove lcov/transit_cov.info '/usr/*' '*src/rpcgen/*' '*src/extern/*' -o lcov/transit_cov_filtered.info
	genhtml lcov/transit_cov_filtered.info -o lcov/report
	@echo "see lcov/report/index.html"

.PHONY: doc
doc:
	asciidoctor-pdf docs/modules/ROOT/pages/index.adoc -o build/design.pdf
	antora generate docsite/site.yml  --to-dir docsite/build/site --stacktrace
dirmake:
	mkdir -p core
	mkdir -p cov
	mkdir -p lcov/report
	mkdir -p build/bin
	mkdir -p build/tests
	mkdir -p build/xdp
	mkdir -p test/trn_func_tests/output
	mkdir -p test/trn_perf_tests/output
