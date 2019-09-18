externsrc = $(wildcard src/extern/*.c)
externobj = $(externsrc:.c=.o)

extern: $(externobj)

$(extenobj): $(externsrc)

libbpf:
	DESTDIR=../../../../lib/ make install -C src/extern/libbpf/src

clean::
	rm -f src/extern/*.o
	rm -f src/extern/*.gcda
	rm -rf lib/*
	make clean -C src/extern/libbpf/src
