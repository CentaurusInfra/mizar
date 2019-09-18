#!/bin/bash

echo "License SPKDX lines:"
find src -type f \( -name "Makefile" -or -name "*.c" -or -name "*.h" -or -name "*.x" -or -name "*.mk" \)  -printf '%p: '  -exec head -n1 {} \; | grep -v 'extern'
