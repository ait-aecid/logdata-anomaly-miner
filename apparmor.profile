# Last Modified: Wed Feb 19 14:58:42 2025
abi <abi/3.0>,

include <tunables/global>

/usr/lib/logdata-anomaly-miner/aminer.py {
  include <abstractions/base>
  include <abstractions/bash>
  include <abstractions/dovecot-common>
  include <abstractions/lightdm>
  include <abstractions/python>

  capability dac_override,

  /usr/bin/dash ix,
  /usr/bin/dpkg-divert mrix,
  /usr/bin/fgrep mrix,
  /usr/bin/python3.12 ix,
  /usr/lib/logdata-anomaly-miner/aminer.py Px,
  /usr/lib/logdata-anomaly-miner/aminer.py r,

}
