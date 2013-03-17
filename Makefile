
PEP8=pep8
PEP8ARG=--ignore=E101,E128,E201,E202,E203,E211,E302,E303,W191,E501
REPO=git@github.com:evilpete/ISYlib-python.git
PROGS=
PLIB=./ISY.py
GIT=git

all:
	echo "Be more exact"

t: style

FILES= ISY/IsyClass.py ISY/IsyExceptionClass.py ISY/IsyNodeClass.py ISY/IsyProgramClass.py ISY/IsyUtilClass.py ISY/IsyVarClass.py __init__.py

syntax:
	python ISY/IsyClass.py
	python ISY/IsyExceptionClass.py
	python ISY/IsyNodeClass.py
	python ISY/IsyProgramClass.py
	python ISY/IsyUtilClass.py
	python ISY/IsyVarClass.py

style: ISY.py syntax
	${PEP8} ${PEP8ARG} ${FILES}


list: 
	egrep -h '^ *class |^ *def |^    ##' ${FILES}

doc: 
	pydoc ${FILES}


lint: 
	pylint ${FILES}


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
