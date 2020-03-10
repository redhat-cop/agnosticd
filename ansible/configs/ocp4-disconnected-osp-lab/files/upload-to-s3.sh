#!/bin/sh
usage()
{
	cat <<USAGE

Usage:
  `basename $0` aws_ak aws_sk bucket srcpath file [mime_type]

Where <arg> is one of:
  aws_ak     access key ('' for upload to public writable bucket)
  aws_sk     secret key ('' for upload to public writable bucket)
  bucket     bucket name
  srcpath    local path prefix to file (end with /, for wd use ./)
  file       rest of path to file and path relative to bucket root
  mime_type  optional mime-type (tries to guess if omitted)

Dependencies:
  To run, this shell script depends on command-line curl and openssl

Example:
  To upload file '~/blog/media/image.png' to bucket 'storage' with
  key (path relative to bucket) 'media/image.png':

    `basename $0` ACCESS SECRET storage ~/blog/ media/image.png

USAGE
	exit 0
}

if [ $# -lt 5 ]; then usage; fi

# Inputs.
aws_ak=$1  # access key
aws_sk=$2  # secret key
bucket=$3  # bucket name
srcpath=$4 # local path prefix to file
file=$5    # rest of path to file and path relative to bucket root
if [ $# -gt 5 ]; then
	mime=$6;
else
	mime=`file -b --mime-type $srcpath$file`
	if [ "$mime" = "text/plain" ]; then
		case $file in
			*.css) mime=text/css;;
			*)     if head $srcpath$file | grep '<html>' >/dev/null; then mime=text/html; fi;;
		esac
	fi
fi

# Generate policy and sign with secret key. Handle GNU and BSD date command style to get tomorrow's date.
p=$(cat <<POLICY | openssl base64
{ "expiration": "`if ! date -v+1d +%Y-%m-%d 2>/dev/null; then date -d tomorrow +%Y-%m-%d; fi`T12:00:00.000Z",
  "conditions": [
    {"acl": "public-read" },
    {"bucket": "$bucket" },
    ["starts-with", "\$key", ""],
    ["starts-with", "\$content-type", ""],
    ["content-length-range", 1, 20971520]
  ]
}
POLICY
)
s=`printf "$p" | openssl sha1 -hmac "$aws_sk" -binary | openssl base64`

# Upload. Supports anonymous upload if bucket is public-writable, and keys are set to ''.
echo "Uploading: $file ($mime) to bucket $bucket"
key_and_sig_args=''
if [ "$aws_ak" != "" ] && [ "$aws_sk" != "" ]; then
    key_and_sig_args="-F AWSAccessKeyId=$aws_ak -F Signature=$s"
fi

curl                            \
    -# -k                       \
    -F key=$file                \
    -F acl=public-read          \
    $key_and_sig_args           \
    -F "Policy=$p"              \
    -F "Content-Type=$mime"     \
    -F file=@$srcpath$file      \
    https://${bucket}.s3.amazonaws.com/ | tee # pass response through tee so curl displays upload progress bar, *and* response