CREATE DATABASE IF NOT EXISTS `agrofrota_tenant`
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON `agrofrota_tenant`.* TO 'agrofrota_runtime'@'%';
