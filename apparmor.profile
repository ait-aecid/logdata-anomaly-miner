abi <abi/3.0>,

include <tunables/global>

 /usr/local/bin/aminerwrapper.sh {
  include <abstractions/base>
  include <abstractions/bash>
  include <abstractions/consoles>
  include <abstractions/dovecot-common>
  include <abstractions/postfix-common>
  include <abstractions/python>

  capability chown,
  capability dac_override,
  capability dac_read_search,

  network inet stream,

  # config files may only be located in allowed locations such as /etc/aminer
  # test with `sudo journalctl -xe | grep DENIED` to adapt the profile for specific needs.

  # Allow temporary files
  /tmp/ rw,
  /tmp/** rwlix,

  # Executables
  /usr/local/bin/aminerwrapper.sh r,
  /usr/bin/aminerwrapper.sh r,
  /usr/bin/python3 ix,
  /usr/bin/python3.* ix,
  /usr/bin/bash ix,
  /usr/bin/basename mrix,
  /usr/bin/lscpu ix,
  /usr/bin/dpkg-divert ix,
  /usr/bin/fgrep rix,
  /usr/bin/grep ix,
  /usr/sbin/cupsd ix,

  # Runtime sockets and directories
  /run/aminer-remote.socket rwkl,
  /run/** rwkl,

  # Application data and libraries
  /**/logdata-anomaly-miner/** rwix,

  # System configuration files
  /etc/aminer/** rw,
  /etc/hosts r,
  /etc/host.conf r,
  /etc/group r,
  /etc/nsswitch.conf r,
  /etc/passwd r,
  /etc/login.defs r,

  # Apt and dpkg related
  /etc/apt/apt.conf.d/** rkl,
  /etc/apt/apt.conf.d/ rkl,
  /usr/share/dpkg/* r,
  /var/lib/dpkg/** r,

  # Application data storage
  /var/lib/aminer/ rwkl,
  /var/lib/aminer/** rwkl,

  # System info and proc/sys
  /proc/ r,
  /proc/** r,
  /sys/** r,

  # Crash reports
  /var/crash/ rw,
  /var/crash/** rwk,

  # Deny sensitive files
  deny /root/** rwklx,
  deny /etc/shadow r,
  deny /etc/sudoers r,
  deny /boot/** r,
}
