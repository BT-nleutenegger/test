#!/bin/bash
#   2013 brain-tec.ch - Cesar Andres
openssl req -new -newkey rsa:1024 -days 365 -nodes -x509 -keyout $1 -out $2 -subj $3