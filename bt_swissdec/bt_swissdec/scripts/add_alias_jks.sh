#!/bin/bash
#   2013 brain-tec.ch - Cesar Andres
keytool -import -trustcacerts -alias $1 -file $2 -keystore $3 -storepass default
