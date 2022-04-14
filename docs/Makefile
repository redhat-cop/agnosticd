# This makefile just reduces keystrokes when building the docs locally :-)
# It is not used by GitHub actions (for that, see .github/workflows).

default:
	asciidoctor -D . --backend=html5 -o index.html README.adoc
