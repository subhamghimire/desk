# Sources

- [Best practices for designing queries](https://docs.aws.amazon.com/redshift/latest/dg/c_designing-queries-best-practices.html) — the query list this subject draws from, one item at a time.
- [Best practices for designing tables](https://docs.aws.amazon.com/redshift/latest/dg/c_designing-tables-best-practices.html) — distribution and sort, which the query advice assumes.
- [EXPLAIN](https://docs.aws.amazon.com/redshift/latest/dg/c_data_redistribution.html) and the redistribution operators (`DS_DIST_NONE`, `DS_DIST_ALL_NONE`, `DS_BCAST_INNER`, `DS_DIST_INNER`, `DS_DIST_BOTH`).
- `SVV_TABLE_INFO.diststyle` — what the table actually is, including when `DISTSTYLE AUTO` has chosen.
