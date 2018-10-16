#!/bin/sh

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
. $SCRIPT_DIR/provision-properties-static.sh
STARTUP_WAIT=180

#First check if the PAM 7 Decision Central REST API is available. We'll wait for 60 seconds
echo "Locating Decision Central REST API."
count=0
launched=false
echo "Trying to connect to spaces URL at: $Decision_CENTRAL_REST_URL/spaces"
until [ $count -gt $STARTUP_WAIT ]
do
  curl -u $USERNAME:$PASSWORD --output /dev/null --silent --head --fail "$DECISION_CENTRAL_REST_URL/spaces"
  if [ $? -eq 0 ] ; then
    echo "PAM 7 Decision Central REST API started."
    launched=true
    break
  fi
  printf '.'
  sleep 5
  let count=$count+5;
done

#Check that the platform has started, otherwise exit.
if [ $launched = "false" ]
then
  echo "PAM 7 Decision Central did not start correctly. Exiting."
  exit 1
else
  echo "PAM 7 Decision Central started."
fi

#CREATE_SPACE_JSON="{ \"name\":\"$SPACE\", \"description\":null, \"projects\":[], \"owner\":\"adminUser\", \"defaultGroupId\":\"$DEFAULT_GROUPID\"}"
CREATE_SPACE_JSON="{ \"name\":\"$SPACE\", \"description\":null, \"projects\":[], \"owner\":\"$USERNAME\", \"defaultGroupId\":\"$DEFAULT_GROUPID\"}"
#Create a space
STATUSCODE=$(curl -H "Accept: application/json" -H "Content-Type: application/json" -f -X POST  -d "$CREATE_SPACE_JSON" -u "$USERNAME:$PASSWORD" --silent --output /dev/null --write-out "%{http_code}" "$DECISION_CENTRAL_REST_URL/spaces")

if [ $STATUSCODE -ne 202 ] ; then
    echo "Error creating new Space. HTTP Status Code: $STATUSCODE. Exiting"
    exit 1
else
    echo "Creating new Space."
fi

# Wait for the space to be created
echo "Waiting for space to be created."
count=0
created=false
until [ $count -gt $STARTUP_WAIT ]
do
  #curl -u adminUser:test1234! --output /dev/null --silent --head --fail "$Decision_CENTRAL_REST_URL/spaces/$SPACE"
  curl -u $USERNAME:$PASSWORD --output /dev/null --silent --head --fail "$DECISION_CENTRAL_REST_URL/spaces/$SPACE"
  if [ $? -eq 0 ] ; then
    echo "\nSpace created."
    created=true
    break
  fi
  printf '.'
  sleep 5
  let count=$count+5;
done

# Give the platform a bit of time before we request the project to be cloned. Not pretty, but don't see another way atm ...
sleep 3

# Check if the project is already present. If it is, we simply skip cloning
#Create a space
curl -u $USERNAME:$PASSWORD --output /dev/null --silent --fail "$DECISION_CENTRAL_REST_URL/spaces/$SPACE/projects/$PROJECT_ID"
if [ $? -ne 0 ] ; then
   echo "Cloning project.."
   # And clone the project into that space
   CLONE_GIT_JSON="{\"name\":\"$PROJECT_ID\", \"gitURL\":\"$PROJECT_GIT\"}"
   #STATUSCODE=$(curl -H "Accept: application/json" -H "Content-Type: application/json" -f -X POST  -d "$CLONE_GIT_JSON" -u "adminUser:test1234!" --silent --output /dev/null --write-out "%{http_code}" "$Decision_CENTRAL_REST_URL/spaces/$SPACE/git/clone")
   STATUSCODE=$(curl -H "Accept: application/json" -H "Content-Type: application/json" -f -X POST  -d "$CLONE_GIT_JSON" -u "$USERNAME:$PASSWORD" --silent --output /dev/null --write-out "%{http_code}" "$DECISION_CENTRAL_REST_URL/spaces/$SPACE/git/clone")
   if [ $STATUSCODE -ne 202 ] ; then
      echo "Error cloning Demo Git repository. Exiting"
      exit 1
   else
      echo "Demo project cloned."
   fi
else
   echo "Project already exists. Not cloning again."
fi
