#!/bin/sh
TESTROOT="tests"
ARTIFACTS="artifacts"
TESTS="${TESTROOT}/unit"
COVERAGE=""
while :
do
  case "$1" in
      -a) TESTS=$TESTROOT ;;
      -c) COVERAGE="--with-coverage --with-xunit --xunit-file=${ARTIFACTS}/tests.xml --cover-erase --cover-package=grok-py"
          mkdir -p $ARTIFACTS;;
      -i) echo "Integration tests are not yet supported. Sorry. :("; exit ;;
      -u) TESTS="${TESTROOT}/unit" ;;
      -r) case "$2" in
              xunit)
                  shift ;

                  if [[ $2 == -* ]]
                    then
                      break;
                  fi

                  if [ $2 ]
                    then
                      RUNID=$2 ;
                    else
                      RUNID=`date + "%Y%m%d%H%M%S"` ;
                  fi

                  RESULTS="tests/results/py/xunit/${RUNID}"
                  mkdir -p $RESULTS
                  XUNIT="--with-xunit --xunit-file=$RESULTS/nosetests.xml";;
              --) break ;;
          esac
          shift ;;
      -*) break ;;
      *) break ;;
      --) break ;;
  esac
  shift
done
shift

nosetests $COVERAGE $XUNIT $TESTS
if [ -n "$COVERAGE" ]; then
    coverage xml
    mv coverage.xml $ARTIFACTS/.
fi
