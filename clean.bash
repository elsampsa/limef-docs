#!/bin/bash
cd "$(dirname "$0")"
cd sphinx  && rm -rf _build generated && cd ..
cd doxygen && rm -rf html latex       && cd ..
