# SOGO users in SQL DB management tool

Simple tool for managing SOGO users in PostgreSQL database and local linux passwd files

- allow bulk import via CSV file
- by default only users with gid==700 (mailusers) and gid==10 (wheel) will be shown
- don't forget to replace 'domain.tld' on your own mail domain
- don't forget to change DB access credentials


Before first run:
  - change group_filter in SOGOUserManager for yours mailusers gid
  - change database user sogo:sogo and DB name 'sogo' as required


Permanent Beta

