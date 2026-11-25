#!/usr/bin/env bash

# Copyright: (c) 2023, Ansible Project
# Apache License, Version 2.0 (see LICENSE.md or https://www.apache.org/licenses/LICENSE-2.0)

# This entrypoint script papers over a number of problems that manifest under different container runtimes when
# using ephemeral UIDs, then chain-execs to the requested init system and/or command. It is an implementation
# detail for the convenience of Ansible execution environments built by ansible-builder.
#
# If we're running as a legit user that has an entry in /etc/passwd and a valid and writeable homedir, we're all good.
#
# If the current uid is not in /etc/passwd, we'll attempt to add it, but /etc/passwd is often not writable by GID 0.
# `ansible-builder` defaults to making /etc/passwd writable by GID0 by default for maximum compatibility, but this is
# not guaranteed. Some runtimes/wrappers (eg podman, cri-o) already create an /etc/passwd entry on the fly as-needed,
# but they may set the homedir to something inaccessible (eg, `/`, WORKDIR).
#
# There are numerous cases where a missing or incorrect homedir in /etc/passwd are fatal. It breaks
# `async` in ansible-core, things like `echo ~someuid`, and numerous other software packages that assume a valid POSIX
# user configuration.
#
# If the homedir listed in /etc/passwd is not writeable by the current user (supposed to be primary GID0), we'll try
# to make it writeable (except `/`), or select another writeable home directory from `$HOME`, `/runner`, or `/tmp` and
# update $HOME (and /etc/passwd if possible) accordingly for the current process chain.
#
# This script is generally silent by default, but some likely-fatal cases will issue a brief warning to stderr. The
# envvars described below can be set before container init to cause faster failures and/or get tracing output.

# options:
# EP_BASH_DEBUG=1 (enable set -x)
# EP_DEBUG_TRACE=1 (enable debug trace to stderr)
# EP_ON_ERROR=ignore/warn/fail (default ignore)

set -eu

if (( "${EP_BASH_DEBUG:=0}" == 1 )); then
  set -x
fi

: "${EP_DEBUG_TRACE:=0}"
: "${EP_ON_ERROR:=warn}"
: "${HOME:=}"
CUR_UID=$(id -u)
CUR_USERNAME=$(id -u -n 2> /dev/null || true)  # whoami-free way to get current username, falls back to current uid

DEFAULT_HOME="/runner"
DEFAULT_SHELL="/bin/bash"

if (( "$EP_DEBUG_TRACE" == 1 )); then
  function log_debug() { echo "EP_DEBUG: $1" 1>&2; }
else
  function log_debug() { :; }
fi

log_debug "entrypoint.sh started"

case "$EP_ON_ERROR" in
  "fail")
    function maybe_fail() { echo "EP_FAIL: $1" 1>&2; exit 1; }
    ;;
  "warn")
    function maybe_fail() { echo "EP_WARN: $1" 1>&2; }
    ;;
  *)
    function maybe_fail() { log_debug "EP_FAIL (ignored): $1"; }
    ;;
esac

function is_dir_writable() {
  [ -d "$1" ] && [ -w "$1" ] && [ -x "$1" ]
}

function ensure_current_uid_in_passwd() {
  log_debug "is current uid ${CUR_UID} in /etc/passwd?"
  
  if ! getent passwd "${CUR_USERNAME}" &> /dev/null ; then
    if [ -w "/etc/passwd" ]; then
      log_debug "appending missing uid ${CUR_UID} into /etc/passwd"
      # use the default homedir; we may have to rewrite it to another value later if it's inaccessible
      echo "${CUR_UID}:x:${CUR_UID}:0:container user ${CUR_UID}:${DEFAULT_HOME}:${DEFAULT_SHELL}" >> /etc/passwd
    else
      maybe_fail "uid ${CUR_UID} is missing from /etc/passwd, which is not writable; this error is likely fatal"
    fi
  else
    log_debug "current uid is already in /etc/passwd"
  fi  
}

function ensure_writeable_homedir() {
  if (is_dir_writable "${CANDIDATE_HOME}") ; then
    log_debug "candidate homedir ${CANDIDATE_HOME} is valid and writeable"
  else
    if [ "${CANDIDATE_HOME}" == "/" ]; then
      log_debug "skipping attempt to fix permissions on / as homedir"
      return 1
    fi

    log_debug "candidate homedir ${CANDIDATE_HOME} is missing or not writeable; attempt to fix"
    if ! (mkdir -p "${CANDIDATE_HOME}" >& /dev/null && chmod -R ug+rwx "${CANDIDATE_HOME}" >& /dev/null) ; then
      log_debug "candidate homedir ${CANDIDATE_HOME} cannot be made writeable"
      return 1
    else
      log_debug "candidate homedir ${CANDIDATE_HOME} was successfully made writeable"
    fi
  fi

  # this might work; export it even if we end up not being able to update /etc/passwd
  # this ensures the envvar matches current reality for this session; future sessions should set automatically if /etc/passwd is accurate
  export HOME=${CANDIDATE_HOME}

  if [ "${CANDIDATE_HOME}" == "${PASSWD_HOME}" ] ; then
    log_debug "candidate homedir ${CANDIDATE_HOME} matches /etc/passwd"
    return 0
  fi

  if ! [ -w /etc/passwd ]; then
    log_debug "candidate homedir ${CANDIDATE_HOME} is valid for ${CUR_USERNAME}, but /etc/passwd is not writable to update it"
    return 1
  fi

  log_debug "resetting homedir for user ${CUR_USERNAME} to ${CANDIDATE_HOME} in /etc/passwd"

  # sed -i wants to create a tempfile next to the original, which won't work with /etc permissions in many cases,
  # so just do it in memory and overwrite the existing file if we succeeded
  NEWPW=$(sed -r "s;(^${CUR_USERNAME}:(.*:){4})(.*:);\1${CANDIDATE_HOME}:;g" /etc/passwd)
  echo "${NEWPW}" > /etc/passwd
}

ensure_current_uid_in_passwd

log_debug "current value of HOME is ${HOME}"

PASSWD_HOME=$(getent passwd "${CUR_USERNAME}" | cut -d: -f6)
log_debug "user ${CUR_USERNAME} homedir from /etc/passwd is ${PASSWD_HOME}"

CANDIDATE_HOMES=("${PASSWD_HOME}" "${HOME}" "${DEFAULT_HOME}" "/tmp")

# we'll set this in the loop as soon as we find a writeable dir
unset HOME

for CANDIDATE_HOME in "${CANDIDATE_HOMES[@]}"; do
  if ensure_writeable_homedir ; then
    break
  fi
done

if ! [ -v HOME ] ; then
  maybe_fail "a valid homedir could not be set for ${CUR_USERNAME}; this is likely fatal"
fi

# We need those directories in order to install collections dynamically with agnosticd
if [ ! -d "/runner/requirements_collections/ansible_collections" ]; then
  mkdir -p /runner/requirements_collections/ansible_collections
  chmod -R ug+rwx /runner/requirements_collections/
fi
export HOME=/home/runner

# Ensure collections path includes all expected locations.
# AAP may override this, so we set it explicitly to include all paths.
if [ -z "${ANSIBLE_COLLECTIONS_PATH:-}" ]; then
  export ANSIBLE_COLLECTIONS_PATH="/home/runner/.ansible/collections:/collections:/usr/share/ansible/collections"
else
  export ANSIBLE_COLLECTIONS_PATH="/home/runner/.ansible/collections:${ANSIBLE_COLLECTIONS_PATH}"
fi

mkdir -p /home/runner/.ansible/collections 2>/dev/null || true
chmod -R ug+rwx /home/runner/.ansible/collections 2>/dev/null || true

log_debug "Original arguments: $*"

export ORIGINAL_ARGUMENTS=("$@")
args=("$@")

# Path to the optional dynamic dependency installer
INSTALL_PLAYBOOK="./ansible/install_dynamic_dependencies.yml"

# Detect Kubernetes environment (container group on OCP/k8s).
# KUBERNETES_SERVICE_HOST is injected by k8s into every pod. If set, we know
# we're running in a container group, not on a bare-metal execution node.
# In this mode, job data (inventory, extravars) arrives via the receptor stdin
# stream after ansible-runner worker starts — it is NOT on disk when the
# entrypoint runs. We install an ansible-playbook wrapper that runs the dynamic
# dependency install after ansible-runner unpacks the job data but before the
# actual playbook is parsed.
if [[ -n "${KUBERNETES_SERVICE_HOST:-}" ]]; then
  log_debug "Kubernetes environment detected. Installing ansible-playbook wrapper."

  WRAPPER_DIR="/runner/.ep-wrapper/bin"
  mkdir -p "${WRAPPER_DIR}"

  cat > "${WRAPPER_DIR}/ansible-playbook" <<'WRAPPER'
#!/usr/bin/env bash
set -eu

REAL_PATH=$(echo "$PATH" | tr ':' '\n' | grep -v '.ep-wrapper' | tr '\n' ':' | sed 's/:$//')
REAL=$(PATH="$REAL_PATH" command -v ansible-playbook)

INSTALL_PLAYBOOK="./ansible/install_dynamic_dependencies.yml"

if [ -z "${_EP_DEPS_INSTALLED:-}" ] && [ -f /runner/env/extravars ] && [ -f "${INSTALL_PLAYBOOK}" ]; then
  export _EP_DEPS_INSTALLED=1
  "${REAL}" "${INSTALL_PLAYBOOK}" \
    -i /runner/inventory/hosts \
    -e @/runner/env/extravars \
    2>&1 || true
fi

exec "${REAL}" "$@"
WRAPPER

  chmod +x "${WRAPPER_DIR}/ansible-playbook"

  export PATH="${WRAPPER_DIR}:${PATH}"

  exec "${ORIGINAL_ARGUMENTS[@]}"
fi

# Detect AAP execution node environment (-u root pattern)
AAP=0
for ((i = 1; i < ${#args[@]}; i++)); do
  if [[ "${args[i]}" == "-u" && "${args[i+1]:-}" == "root" ]]; then
    AAP=1
    break
  fi
done

if (( AAP == 1 )); then
  log_debug "AAP environment detected. Running with fixed extra-vars"
  if [ -f "${INSTALL_PLAYBOOK}" ]; then
    /usr/local/bin/ansible-playbook "${INSTALL_PLAYBOOK}" -i /runner/inventory/hosts -e @/runner/env/extravars
  else
    log_debug "Install playbook ${INSTALL_PLAYBOOK} not found, skipping dynamic dependency install"
  fi
else
  shift 2
  log_debug "Non-AAP environment. Running with processed arguments"
  log_debug "Remaining arguments: $*"
  if [ -f "${INSTALL_PLAYBOOK}" ]; then
    /usr/local/bin/ansible-playbook "${INSTALL_PLAYBOOK}" "$@"
  else
    log_debug "Install playbook ${INSTALL_PLAYBOOK} not found, skipping dynamic dependency install"
  fi
fi

log_debug "chain exec-ing requested command: ${ORIGINAL_ARGUMENTS[*]}"
exec "${ORIGINAL_ARGUMENTS[@]}"
