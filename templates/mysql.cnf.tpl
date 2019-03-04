[mysqld]
user		= mysql
pid-file	= /var/run/mysqld/mysqld.pid
socket		= /var/run/mysqld/mysqld.sock
port		= {port}
datadir		= /var/lib/mysql
tmpdir		= /tmp
lc-messages-dir	= /usr/share/mysql/english/
skip-external-locking
skip-character-set-client-handshake
default-storage-engine = {engine}
character-set-server = {charset}
init-connect='SET NAMES {charset}'
transaction-isolation = READ-COMMITTED
