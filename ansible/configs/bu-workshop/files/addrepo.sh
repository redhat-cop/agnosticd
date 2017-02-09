#!/bin/sh
#
# Sonatype nexus Rest API: https://oss.sonatype.org/nexus-restlet1x-plugin/default/docs/index.html
#
# addrepo.sh jboss http://maven.repository.redhat.com/techpreview/all/
# addrepo.sh jboss-ce https://repository.jboss.org/nexus/content/groups/public/
#
TEMPLATE_FILE="/tmp/repo.json"

if [ ! -x "$HOME/jq" ]
then
curl --fail --silent --location --retry 3 \
    https://github.com/stedolan/jq/releases/download/jq-1.5/jq-linux64 \
    -o $HOME/jq \
    && chmod 755 $HOME/jq
fi

: ${NEXUS_USER:="admin"}
: ${NEXUS_PASSWORD:="admin123"}
: ${NEXUS_BASE_URL:="http://localhost:8081"} # Avoid trailing slash

read -d '' TEMPLATE << EOF
{
   "data": {
      "repoType": "proxy",
      "id": "%ID%",
      "name": "%ID%",
      "browseable": true,
      "indexable": true,
      "notFoundCacheTTL": 1440,
      "artifactMaxAge": -1,
      "metadataMaxAge": 1440,
      "itemMaxAge": 1440,
      "repoPolicy": "RELEASE",
      "provider": "maven2",
      "providerRole": "org.sonatype.nexus.proxy.repository.Repository",
      "downloadRemoteIndexes": false,
      "autoBlockActive": true,
      "fileTypeValidation": true,
      "exposed": true,
      "checksumPolicy": "WARN",
      "remoteStorage": {
         "remoteStorageUrl": "%REPO%",
         "authentication": null,
         "connectionSettings": null
      }
   }
}
EOF


function usage {
   echo "You have to pass a repo ID and a remote repo URL"
}

[ "$#" -ne 2 ] && usage && exit 0

repoID=$1
repoURL=$2
# Verify that nexus server is running on port 8081 internally, otherwise fail
# TODO:

function sedeasy {
  echo "[DEBUG] sed -i \"s/$(echo $1 | sed -e 's/\([[\/.*]\|\]\)/\\&/g')/$(echo $2 | sed -e 's/[\/&]/\\&/g')/g\" $3"
  sed -i "s/$(echo $1 | sed -e 's/\([[\/.*]\|\]\)/\\&/g')/$(echo $2 | sed -e 's/[\/&]/\\&/g')/g" $3
}

# This function will load into http://localhost:8081/nexus the appropriate configuration
# and extract the zip file into the data_volume_container
#
# Arguments:
#    repoID
#    repoURL
#
function loadRepo {
   local _id=$1
   local _url=$2
   local _exit=0

   # Replace the ID token with the name of the zip file (without .zip) and replace in template
   echo "$TEMPLATE" > $TEMPLATE_FILE
   sedeasy "%ID%" "$_id" $TEMPLATE_FILE
   sedeasy "%REPO%" "$_url" $TEMPLATE_FILE

   echo "[INFO] Sending the following template for creating repo $_id"
   cat $TEMPLATE_FILE

   # Create repository configuration
   echo "curl -H 'Accept: application/json' -H 'Content-Type: application/json' -f -X POST -v -d \"@$TEMPLATE_FILE\" -u \"${NEXUS_USER}:${NEXUS_PASSWORD}\" \"${NEXUS_BASE_URL}/service/local/repositories\""
   curl -H "Accept: application/json" -H "Content-Type: application/json" -f -X POST -v -d "@$TEMPLATE_FILE" -u "${NEXUS_USER}:${NEXUS_PASSWORD}" "${NEXUS_BASE_URL}/service/local/repositories"

   # TODO: Instead of failing, check if the repository exist.
   _exit=$?
   [ $_exit -ne 0 ] && echo "[WARN] Error creating the hosted repository for $_id" && exit $_exit
   echo ""
   echo "[INFO] Repository created"

   # Adding repository configuration to public group.
   # We first query for current config and write it into a /tmp/group.json file
   echo "[INFO] Getting information about public group"
   curl -s -H "Accept: application/json" -H "Content-Type: application/json" -f -X GET -u "${NEXUS_USER}:${NEXUS_PASSWORD}" -o /tmp/group.json "${NEXUS_BASE_URL}/service/local/repo_groups/public"
   [ $_exit -ne 0 ] && echo "[WARN] Error getting public group repository information" && exit $_exit
   echo ""
   echo "[INFO] Public repo information retrieved"


   # then we add repository id
   echo "[INFO] Add information about this repository to the public group"
   $HOME/jq '.' /tmp/group.json > /tmp/group-pretty.json
   # We inset the repository in the group just before central and 3rdparty
   sed -i -e "`wc -l /tmp/group-pretty.json | awk '{s=$1-13} END {print s}'` a\{\"id\":\"$_id\"}," /tmp/group-pretty.json
   echo ""
   echo "[INFO] Information about this repository added to the public group"

   [ ! -f /tmp/group-pretty.json ] && echo "[WARN] Something failed while trying to add the repository to the public group. Do it manually" && exit 2
   # and we load the new configuration for public group

   echo "[INFO] Updating the public repo"
   curl -H "Accept: application/json" -H "Content-Type: application/json" -f -X PUT  -v -d "@/tmp/group-pretty.json" -u "${NEXUS_USER}:${NEXUS_PASSWORD}" "${NEXUS_BASE_URL}/service/local/repo_groups/public"
   [ $_exit -ne 0 ] && echo "[WARN] Error adding the hosted repository for $_id to the public group" && exit $_exit
   echo ""
   echo "[INFO] Public group updated"

   echo "------"
   echo "------"
   echo "------"
   echo "Repository loaded with name $_id and added into public group"
   echo "------"
   echo "------"
   echo "------"
}


echo "Loading $repoID hosting $repoURL"
loadRepo "$repoID" "$repoURL"
