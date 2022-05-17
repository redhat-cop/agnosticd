Role Name
=========

gcp-get-token

Role Description
================

This role does the following:
- Sets up a JWT assersion to get a auth token from GCP

Requirements
------------

Role Variables
--------------

gcp_credentials - json from GCP service account key

EXAMPLE:
gcp_credentials: '
{
  "type": "service_account",
  "project_id": "project-12335",
  "private_key_id": "asdfasdfasdfasdf",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMII.....RSA KEY WITHOUT LINEBREAKS\n-----END PRIVATE KEY-----\n",
  "client_email": "myuser@project-12335.iam.gserviceaccount.com",
  "client_id": "123454",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/myuser%40project-12335.iam.gserviceaccount.com"
}
'

Output
------

auth_response - response from the GCP API
auth_response.json.access_token - usable token for direct API calls to GCP


Dependencies
------------

License
-------

BSD

Authors Information
------------------
prutledg@redhat.com
