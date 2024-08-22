#!/usr/bin/env python3


# This script gets the output dir object from the agnosticd-output-dir bucket and then saves it in /tmp/output-dir-$uuid

# The name of the s3 bucket is by default agnosticd-output-dir, otherwise it's passed as the --bucket arg

bucket = "agnosticd-output-dir"

import boto3

import argparse

parser = argparse.ArgumentParser(description='Get the output dir object from the agnosticd-output-dir bucket and then save it in /tmp/output-dir-$uuid')

parser.add_argument('--bucket', help='The name of the s3 bucket to get the output dir object from. Default is agnosticd-output-dir', default="agnosticd-output-dir")



# The uuid is passed as the --uuid arg

parser.add_argument('--uuid', help='The uuid of the output dir object to get', required=True)

# the guid is passed as the --guid arg

parser.add_argument('--guid', help='The guid of the output dir object to get', required=True)


args = parser.parse_args()

s3 = boto3.resource('s3')

bucket = s3.Bucket(args.bucket)


# The object is in the format:
# "{{ guid }}_{{ uuid }}.tar.gz"

object = args.guid + "_" + args.uuid + ".tar.gz"

try:
    bucket.download_file(object, "/tmp/output-dir-" + args.uuid + ".tar.gz")

    print("Downloaded /tmp/output-dir-" + args.uuid + ".tar.gz")

except Exception as e:
    print(e)
    print("Could not download /tmp/output-dir-" + args.uuid + ".tar.gz")

    exit(1)
