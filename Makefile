TOPDIR = $(shell pwd)

all:	clean a2event a2upload a2task

a2event:
	cd ${TOPDIR}/cmd/event && go build -o ${TOPDIR}/build/a2event

a2upload:
	cd ${TOPDIR}/cmd/calls_upload && go build -o ${TOPDIR}/build/a2upload

a2task:
	cd ${TOPDIR}/cmd/task && go build -o ${TOPDIR}/build/a2task


.PHONY: clean
clean:
	rm -f build/*

