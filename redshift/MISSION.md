# Redshift query design

Write queries that Redshift can run without moving rows that did not need to move, and read an EXPLAIN plan well enough to see that before the query runs.

Done looks like: given a table's distribution and sort, predict the expensive step, then change the query or the table so that step disappears.
