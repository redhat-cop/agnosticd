KEY_GRIP1=$(gpg-connect-agent -q 'keyinfo --list' /bye | awk '/KEYINFO/ { print $3 }' | head -1)
KEY_GRIP2=$(gpg-connect-agent -q 'keyinfo --list' /bye | awk '/KEYINFO/ { print $3 }' | tail -1)
/usr/libexec/gpg-preset-passphrase -c $KEY_GRIP1 <<< openshift
/usr/libexec/gpg-preset-passphrase -c $KEY_GRIP2 <<< openshift