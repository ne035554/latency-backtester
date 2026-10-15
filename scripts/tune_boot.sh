#!/usr/bin/env bash
# Isolates CPUs from the Linux scheduler at boot. Requires a reboot afterwards.
# Usage: sudo ./scripts/tune_boot.sh 2,3
set -euo pipefail
CPUS="${1:?give the CPU list to isolate, e.g. 2,3}"

# Files in /etc/default/grub.d/ are read after /etc/default/grub, so this one appends to whatever is set already
cat > /etc/default/grub.d/99-isolation.cfg <<CFG
GRUB_CMDLINE_LINUX_DEFAULT="\$GRUB_CMDLINE_LINUX_DEFAULT isolcpus=${CPUS} nohz_full=${CPUS} rcu_nocbs=${CPUS}"
CFG

update-grub
echo "Done. Now run: sudo reboot"
