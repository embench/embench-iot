#!/bin/sh

# Script to generate a table of contents for Markdown user guide.

# Copyright (C) 2019 Embecosm Limited
#
# Contributor: Jeremy Bennett <jeremy.bennett@embecosm.com>
# Contributor: Roger Shepherd <rog@rcjd.net>
#
# This file is part of Embench.

# SPDX-License-Identifier: GPL-3.0-or-later

tmpf=/tmp/mdtoc$$.md

# Function to convert a section header to an anchor and output as a link to
# the section anchor. Rules are:
# - any character other than ' .-_[0-9][A-Z][a-z]' is deleted
# - all remaining upper case characters are converted to lower case
# - all spaces are convered to hyphens.

mangle2 ()
{
    while read h
    do
	htxt=$(echo ${h} | sed -e 's/###\{0,1\} //')
	hnospc=$(echo ${htxt} |  tr -c -d "[:alnum:]_. -" |
		 tr 'ABCDEFGHIJKLMNOPQRSTUVWXYZ ' 'abcdefghijklmnopqrstuvwxyz-')
	if echo ${h} | grep -q '^## '
	then
	    printf "%s [%s](#%s)\n" "-" "$htxt" "$hnospc"
	else
	    printf "    - [%s](#%s)\n" "$htxt" "$hnospc"
	fi
    done
}

# Copy the preamble to the document

sed < README.md > ${tmpf} \
    -n -e '1,/Insert ToC here/p'

echo >> ${tmpf}

# Generate the ToC block

sed < README.md -n -e '/End of ToC insertion/,$p' |
    sed -n -e '/^###\{0,1\} /p' |
    mangle2 >> ${tmpf}

# And copy in the rest of the document

echo >> ${tmpf}

sed < README.md >> ${tmpf} \
    -n -e '/End of ToC insertion/,$p'

mv README.md README.md.old
mv ${tmpf} README.md
