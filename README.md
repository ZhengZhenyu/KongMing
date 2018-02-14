# KongMing
Compute agent work with OpenStack Nova to achieve optimized NUMA allocations

## Idea
In NFV cloud scenario, performance is very important. Users often request
to allocate the CPUs and RAM to the same NUMA for better performance. For
some advanced NFV users, they have their own orchestrator, calculating the
most suitable instance allocations based on their own mechanism. In some
cases, they want to tell the cloud platform exactly where they want the
instances to be, to reach the most optimized resource usage. This is obvious
not "cloudy", but it is also obvious this is a key feature for NFV users.
So we decide to make an agent outside of the cloud platform, for example
OpenStack, to adjust the CPU and RAM allocations based on user demands after
the instances were successfully launched. This will not against the cloud
platforms mission, but also do the work.
