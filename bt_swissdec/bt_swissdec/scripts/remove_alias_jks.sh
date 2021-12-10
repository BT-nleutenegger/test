#!/bin/bash
#   2013 brain-tec.ch - Cesar Andres
keytool -delete -alias $1 -keystore $2 -storepass default
