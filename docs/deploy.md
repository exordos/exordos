# Updating core from a local build

Run `exordos deploy --element-dir output --element core --timeout 1800`
from the build host. Deploy upgrades the installed core and waits for the new
version to become ACTIVE. During a core restart, connection failures and
HTTP 502/503/504 responses are retried until the timeout; interrupted polls
reset the consecutive ACTIVE checks. If the timeout expires, inspect the core
VM and its bootstrap logs before starting another deployment.
