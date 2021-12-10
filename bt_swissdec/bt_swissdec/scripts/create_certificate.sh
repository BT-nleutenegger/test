#!/bin/bash
#   2013 brain-tec.ch - Cesar Andres
keytool -genkey -alias test -keyalg RSA -keystore $1 -keysize 2048