#!/bin/bash
echo "Content-type: text/html"
echo ""
echo "<html><body>CGI Bash Bug Example</body></html>"
echo `df -h / | grep -v Filesystem`
