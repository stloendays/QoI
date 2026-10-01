# Sequential-QSQ writer integration

This layer integrates the accepted WP-H optimization with the frozen WP-E certifying-writer decisions without changing any scientific decision.

The frozen WP-E analysis assigns a fixed cost of six Bader solves to QSQ for every material: one reference plus five probes. WP-H replaces this execution cost with one reference plus probes evaluated in the frozen order until the first response reaches the requested tolerance.

The integration script:
1. reads the original WP-E `policy_material.csv`;
2. reconstructs exact sequential-QSQ cost from the frozen per-seed QSQ responses;
3. asserts 254/254 eligibility equivalence at every threshold;
4. preserves every returned codec, tolerance, stored size, certificate and oracle comparison;
5. changes only the solve-count columns.

At the primary `1e-3 e` contract and adopted BISECT policy, mean end-to-end cost over all 254 development materials is 12.004 -> 10.339 Bader solves/material (-13.9%), with unchanged archive CR 14.899 and zero misses.

This is an execution optimization, not a new QSQ definition.
