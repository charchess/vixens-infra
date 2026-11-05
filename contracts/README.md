# Contract boundary

Infra consumes Core contracts and may publish shared service contracts such as PostgreSQL, identity or observability after they are explicitly defined.

The canonical dependency graph and multi-repository resolution will be defined through Vixens issues #3588, #3960 and #4513. This bootstrap deliberately does not invent a second contract registry.
