#!/usr/bin/env bash
# Runtime tuning that does not need a reboot. Re-run it after every reboot.
# Usage: sudo ./scripts/tune_runtime.sh 0,1
#   the argument is the list of housekeeping CPUs that should handle interrupts (never the isolated ones)
set -uo pipefail
HOUSE="${1:?give the housekeeping CPU list, e.g. 0,1}"

# 1. Low latency power and scheduler profile
systemctl enable --now tuned
tuned-adm profile latency-performance
echo "tuned profile: $(tuned-adm active)"

# 2. Stop the IRQ balancer so it does not move interrupts back onto isolated CPUs
systemctl stop irqbalance 2>/dev/null || true

# 3. Send every movable hardware interrupt to the housekeeping CPUs only
moved=0
for f in /proc/irq/*/smp_affinity_list; do
  if echo "$HOUSE" > "$f" 2>/dev/null; then moved=$((moved + 1)); fi
done
echo "IRQs moved to CPUs $HOUSE: $moved (some IRQs cannot be moved; that is normal)"
