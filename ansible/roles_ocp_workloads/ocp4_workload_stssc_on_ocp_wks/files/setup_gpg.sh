cat <<EOF > ~/genkey
Key-Type: 1
Key-Length: 4096
Subkey-Type: 1
Subkey-Length: 4096
Name-Real: dev-user
Name-Email: dev-user@opentlc.com
Expire-Date: 0
Passphrase: openshift
EOF
gpg --gen-key --batch ~/genkey
KEY_ID=$(gpg --list-keys --keyid-format LONG | grep 'pub ' | awk '{print $2}' | cut -d'/' -f2)
git config --global user.name dev-user
git config --global user.email dev-user@opentlc.com
git config --global commit.gpgsign true
git config --global user.signingkey $KEY_ID
cat <<EOF > ~/.gnupg/gpg-agent.conf
allow-preset-passphrase
allow-loopback-pinentry
EOF
cat <<EOF > ~/.gpg
#!/usr/bin/bash

sh ~/init_gpg_passphrase.sh
gpg --pinentry-mode loopback \$@
EOF
chmod +x ~/.gpg
gpg-connect-agent reloadagent /bye
git config --global gpg.program ~/.gpg