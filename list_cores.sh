#!/bin/bash
# MIT License
 
# Copyright (c) 2023 Advanced Micro Devices, Inc.
 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
set -x

if test $# -ne 6
then
	echo "usage ./script {#CORES PER CCD} {#CCDS per SOCKET} {$ SOCKETS IN SYSTEM} {CCD # | quart0 | quart1 | quart2 | quart3 | half0 | half1 | all} {THREAD: 0 or 1} {SOCKET_TO_LIST: 0, 1 or all}"
	exit 0
fi

CORES_PER_CCD=$1
CCD_NUM=$2
SOCKET_NUM=$3
CCD=$4
THREAD=$5
SOCKET_TO_LIST=$6

CORES_PER_SOCKET=`expr $CORES_PER_CCD \* $CCD_NUM`
HALF_CORES_PER_SOCKET=`expr $CORES_PER_SOCKET / 2`
QUARTER_CORES_PER_SOCKET=`expr $CORES_PER_SOCKET / 4`
SMT_OFFSET=`expr $CORES_PER_SOCKET \* $SOCKET_NUM`
CORES_PER_THREAD=`expr $CORES_PER_SOCKET \* $SOCKET_NUM`

LIST=""






if test $CCD = all
then

	if [ $SOCKET_TO_LIST = 0 ] || [ $SOCKET_TO_LIST = all ]
	then

		NCORES=0
		CORE_i=`expr $THREAD \* $CORES_PER_THREAD`
		while test $NCORES -ne $CORES_PER_SOCKET
		do
			LIST=`echo $LIST$CORE_i,`
			CORE_i=`expr $CORE_i + 1`
			NCORES=`expr $NCORES + 1`
		done

	fi

	if ([ $SOCKET_TO_LIST = 1 ] || [ $SOCKET_TO_LIST = all ]) && [ $SOCKET_NUM = 2 ]
	then

		NCORES=0
		CORE_i=`expr $THREAD \* $CORES_PER_THREAD + $CORES_PER_SOCKET`
		while test $NCORES -ne $CORES_PER_SOCKET
		do
			LIST=`echo $LIST$CORE_i,`
			CORE_i=`expr $CORE_i + 1`
			NCORES=`expr $NCORES + 1`
		done

	fi

elif test $CCD = half0
then

	if [ $SOCKET_TO_LIST = 0 ] || [ $SOCKET_TO_LIST = all ]
	then

		NCORES=0
		CORE_i=`expr $THREAD \* $CORES_PER_THREAD`
		while test $NCORES -ne $HALF_CORES_PER_SOCKET
		do
			LIST=`echo $LIST$CORE_i,`
			CORE_i=`expr $CORE_i + 1`
			NCORES=`expr $NCORES + 1`
		done

	fi

	if ([ $SOCKET_TO_LIST = 1 ] || [ $SOCKET_TO_LIST = all ]) && [ $SOCKET_NUM = 2 ]
	then

		NCORES=0
		CORE_i=`expr $THREAD \* $CORES_PER_THREAD + $CORES_PER_SOCKET`
		while test $NCORES -ne $HALF_CORES_PER_SOCKET
		do
			LIST=`echo $LIST$CORE_i,`
			CORE_i=`expr $CORE_i + 1`
			NCORES=`expr $NCORES + 1`
		done

	fi

elif test $CCD = half1
then

	if [ $SOCKET_TO_LIST = 0 ] || [ $SOCKET_TO_LIST = all ]
	then

		NCORES=0
		CORE_i=`expr $THREAD \* $CORES_PER_THREAD + $HALF_CORES_PER_SOCKET`
		while test $NCORES -ne $HALF_CORES_PER_SOCKET
		do
			LIST=`echo $LIST$CORE_i,`
			CORE_i=`expr $CORE_i + 1`
			NCORES=`expr $NCORES + 1`
		done

	fi

	if ([ $SOCKET_TO_LIST = 1 ] || [ $SOCKET_TO_LIST = all ]) && [ $SOCKET_NUM = 2 ]
	then

		NCORES=0
		CORE_i=`expr $THREAD \* $CORES_PER_THREAD + $CORES_PER_SOCKET + $HALF_CORES_PER_SOCKET`
		while test $NCORES -ne $HALF_CORES_PER_SOCKET
		do
			LIST=`echo $LIST$CORE_i,`
			CORE_i=`expr $CORE_i + 1`
			NCORES=`expr $NCORES + 1`
		done

	fi

elif test $CCD = quart0
then

	if [ $SOCKET_TO_LIST = 0 ] || [ $SOCKET_TO_LIST = all ]
	then

		NCORES=0
		CORE_i=`expr $THREAD \* $CORES_PER_THREAD`
		while test $NCORES -ne $QUARTER_CORES_PER_SOCKET
		do
			LIST=`echo $LIST$CORE_i,`
			CORE_i=`expr $CORE_i + 1`
			NCORES=`expr $NCORES + 1`
		done

	fi

	if ([ $SOCKET_TO_LIST = 1 ] || [ $SOCKET_TO_LIST = all ]) && [ $SOCKET_NUM = 2 ]
	then

		NCORES=0
		CORE_i=`expr $THREAD \* $CORES_PER_THREAD + $CORES_PER_SOCKET`
		while test $NCORES -ne $QUARTER_CORES_PER_SOCKET
		do
			LIST=`echo $LIST$CORE_i,`
			CORE_i=`expr $CORE_i + 1`
			NCORES=`expr $NCORES + 1`
		done

	fi

elif test $CCD = quart1
then

	if [ $SOCKET_TO_LIST = 0 ] || [ $SOCKET_TO_LIST = all ]
	then

		NCORES=0
		CORE_i=`expr $THREAD \* $CORES_PER_THREAD + $QUARTER_CORES_PER_SOCKET`
		while test $NCORES -ne $QUARTER_CORES_PER_SOCKET
		do
			LIST=`echo $LIST$CORE_i,`
			CORE_i=`expr $CORE_i + 1`
			NCORES=`expr $NCORES + 1`
		done

	fi

	if ([ $SOCKET_TO_LIST = 1 ] || [ $SOCKET_TO_LIST = all ]) && [ $SOCKET_NUM = 2 ]
	then

		NCORES=0
		CORE_i=`expr $THREAD \* $CORES_PER_THREAD + $CORES_PER_SOCKET + $QUARTER_CORES_PER_SOCKET`
		while test $NCORES -ne $QUARTER_CORES_PER_SOCKET
		do
			LIST=`echo $LIST$CORE_i,`
			CORE_i=`expr $CORE_i + 1`
			NCORES=`expr $NCORES + 1`
		done

	fi

elif test $CCD = quart2
then

	if [ $SOCKET_TO_LIST = 0 ] || [ $SOCKET_TO_LIST = all ]
	then

		NCORES=0
		CORE_i=`expr $THREAD \* $CORES_PER_THREAD + $HALF_CORES_PER_SOCKET`
		while test $NCORES -ne $QUARTER_CORES_PER_SOCKET
		do
			LIST=`echo $LIST$CORE_i,`
			CORE_i=`expr $CORE_i + 1`
			NCORES=`expr $NCORES + 1`
		done

	fi

	if ([ $SOCKET_TO_LIST = 1 ] || [ $SOCKET_TO_LIST = all ]) && [ $SOCKET_NUM = 2 ]
	then

		NCORES=0
		CORE_i=`expr $THREAD \* $CORES_PER_THREAD + $CORES_PER_SOCKET + $HALF_CORES_PER_SOCKET`
		while test $NCORES -ne $QUARTER_CORES_PER_SOCKET
		do
			LIST=`echo $LIST$CORE_i,`
			CORE_i=`expr $CORE_i + 1`
			NCORES=`expr $NCORES + 1`
		done

	fi

elif test $CCD = quart3
then

	if [ $SOCKET_TO_LIST = 0 ] || [ $SOCKET_TO_LIST = all ]
	then

		NCORES=0
		CORE_i=`expr $THREAD \* $CORES_PER_THREAD + $HALF_CORES_PER_SOCKET + $QUARTER_CORES_PER_SOCKET`
		while test $NCORES -ne $QUARTER_CORES_PER_SOCKET
		do
			LIST=`echo $LIST$CORE_i,`
			CORE_i=`expr $CORE_i + 1`
			NCORES=`expr $NCORES + 1`
		done

	fi

	if ([ $SOCKET_TO_LIST = 1 ] || [ $SOCKET_TO_LIST = all ]) && [ $SOCKET_NUM = 2 ]
	then

		NCORES=0
		CORE_i=`expr $THREAD \* $CORES_PER_THREAD + $CORES_PER_SOCKET + $HALF_CORES_PER_SOCKET + $QUARTER_CORES_PER_SOCKET`
		while test $NCORES -ne $QUARTER_CORES_PER_SOCKET
		do
			LIST=`echo $LIST$CORE_i,`
			CORE_i=`expr $CORE_i + 1`
			NCORES=`expr $NCORES + 1`
		done

	fi

else

	if [ $SOCKET_TO_LIST = 0 ] || [ $SOCKET_TO_LIST = all ]
	then

		NCORES=0
		CORE_i=`expr $CCD \* $CORES_PER_CCD + $THREAD \* $CORES_PER_THREAD`
		while test $NCORES -ne $CORES_PER_CCD
		do
			LIST=`echo $LIST$CORE_i,`
			CORE_i=`expr $CORE_i + 1`
			NCORES=`expr $NCORES + 1`
		done

	fi

	if ([ $SOCKET_TO_LIST = 1 ] || [ $SOCKET_TO_LIST = all ]) && [ $SOCKET_NUM = 2 ]
	then

		NCORES=0
		CORE_i=`expr $CCD \* $CORES_PER_CCD + $THREAD \* $CORES_PER_THREAD + $CORES_PER_SOCKET`
		while test $NCORES -ne $CORES_PER_CCD
		do
			LIST=`echo $LIST$CORE_i,`
			CORE_i=`expr $CORE_i + 1`
			NCORES=`expr $NCORES + 1`
		done

	fi

fi

echo $LIST | sed "s/,/ /g"
