#!/bin/bash

if [ -e "$1.py" ]; then
    echo -e "\nFile $1 already exists .. exiting now\n"
else
    echo -e "#!/usr/bin/env python3\n\n" > "$1.py"
    chmod +x "$1.py"
fi
