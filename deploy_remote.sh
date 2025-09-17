#!/usr/bin/env bash
DEST_DIR="/usr/local/sbin"
TMP_DIR="/tmp"

FILES=(
  "dist/autostart.pyz"
  "dist/configurator.pyz"
  "dist/installer.pyz"
)

echo -n "Server host: "
read SERVER_HOST

echo -n "Server user: "
read SERVER_USER

echo -n "Server data dir: "
read SERVER_DATA_DIR

echo -n "Server password: "
read -s password
echo

DATA_DIR="/usr/local/share/${SERVER_DATA_DIR}"

echo "Deploying data folder"
sshpass -p "$password" scp -r "./data" "${SERVER_USER}@${SERVER_HOST}:${TMP_DIR}/data"
sshpass -p "$password" ssh -t "${SERVER_USER}@${SERVER_HOST}" "
  set -euo pipefail
  echo "$password" | sudo -S rm -rf "${DATA_DIR}"
  echo "$password" | sudo -S install -d -m 0755 "${DATA_DIR}"
  echo "$password" | sudo -S cp -a ${TMP_DIR}/data "${DATA_DIR}"
  echo "$password" | sudo -S rm -rf ${TMP_DIR}/data
  echo "$password" | sudo -S find "${DATA_DIR}/data" -type d -exec chmod 0755 {} +
  echo "$password" | sudo -S find "${DATA_DIR}/data" -type f -exec chmod 0644 {} +
  echo "$password" | sudo -S chown -R root:root "${DATA_DIR}"
"
echo "Deploying data folder done"

for f in "${FILES[@]}"; do
  fileName=${f//dist\//}

  echo "Deploying file $f"
  sshpass -p "$password" scp -r "$f" "${SERVER_USER}@${SERVER_HOST}:${TMP_DIR}/${fileName}"

  echo "[*] Installing..."
  sshpass -p "$password" ssh -t "${SERVER_USER}@${SERVER_HOST}" "
    set -euo pipefail
    echo "$password" | sudo -S -k install -m 0755 -o root -g root '${TMP_DIR}/${fileName}' '${DEST_DIR}/${fileName}'
    echo "$password" | sudo -S rm -f '${TMP_DIR}/${fileName}'
  "
done
echo "[+] Done"