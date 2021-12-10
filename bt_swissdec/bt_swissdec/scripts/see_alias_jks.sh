#!/bin/bash
#   2013 brain-tec.ch - Cesar Andres
keytool -list -v -keystore $1 -storepass default | grep Alias
