unseal() {
    echo "unsealing..."
    vault operator unseal -tls-skip-verify $(grep -A 5 unseal_keys_b64 /vault/data/vault-auto-unseal-keys.txt |head -2|tail -1|sed 's/- //g')
    vault operator unseal -tls-skip-verify $(grep -A 5 unseal_keys_b64 /vault/data/vault-auto-unseal-keys.txt |head -3|tail -1|sed 's/- //g')
    vault operator unseal -tls-skip-verify $(grep -A 5 unseal_keys_b64 /vault/data/vault-auto-unseal-keys.txt |head -4|tail -1|sed 's/- //g')
}

FILE=/vault/data/vault-auto-unseal-keys.txt
if [ ! -f "$FILE" ]; then
    exit 0
fi

vault status
RESULT=$?
if [ $RESULT -eq 0 ];
then
    exit 0
fi

if [ $RESULT -eq 2 ];
then
    unseal
    exit 0
else
    while [$RESULT -ne 0]; do
        sleep 5s
        vault status
        RESULT=$?
    done
    unseal
    exit $RESULT
fi