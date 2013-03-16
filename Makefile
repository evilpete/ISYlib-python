
PEP8=pep8
PEP8ARG=--ignore=E101,E128,E201,E202,E203,E211,E302,E303,W191,E501
REPO=git@github.com:evilpete/ISYlib-python.git
PROGS=
PLIB=./ISY.py
GIT=git

all:
	echo "Be more exact"

t: style


syntax: ISY.py
	python ./ISY.py

style: ISY.py syntax
	${PEP8} ${PEP8ARG} ./ISY.py


list: ISY.py
	egrep '^ *class |^ *def |^    ##' ISY.py

doc: ISY.py
	pydoc ./ISY.py




#checkall: ${PLIB} ${PROGS}
#	for targ in $? ; do \
#	    ${PERL} -cW $$targ ; \
#	done

checkin: commit push

commit:
	${GIT} commit -a

push:
	${GIT} push

pull:
	${GIT} pull


${PLBS}:
	@echo ${GIT} pull
