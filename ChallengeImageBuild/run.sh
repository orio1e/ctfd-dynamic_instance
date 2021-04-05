#!/bin/bash
service apache2 start 
service mysql start
service ssh start
a2enmod rewrite

#rm /var/www/html/index.html /var/www/html/phpinfo.php
chown www-data:www-data /var/www/html/* -R
cd /var/www/html
chmod -R 777 /var/www/html
sleep 2
/bin/bash