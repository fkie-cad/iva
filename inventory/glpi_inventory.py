import traceback
from contextlib import closing
import pymysql.cursors
import config
import logger

SQL_QUERY = "SELECT DISTINCT `glpi_softwares`.`name` AS product, `glpi_softwareversions`.`name` AS version, " \
            "`glpi_manufacturers`.`name` AS vendor " \
            "FROM `glpi_computers_softwareversions` " \
            "INNER JOIN `glpi_softwareversions` " \
            "ON (`glpi_computers_softwareversions`.`softwareversions_id` = `glpi_softwareversions`.`id`) " \
            "INNER JOIN `glpi_softwares` ON (`glpi_softwareversions`.`softwares_id` = `glpi_softwares`.`id`) " \
            "LEFT  JOIN `glpi_manufacturers` " \
            "ON (`glpi_softwares`.`manufacturers_id` = `glpi_manufacturers`.`id`) " \
            "WHERE `glpi_computers_softwareversions`.`is_deleted_computer` = '0' " \
            "AND `glpi_computers_softwareversions`.`is_template_computer` = '0' " \
            "AND `glpi_computers_softwareversions`.`is_deleted` = '0' " \
            "AND `glpi_softwares`.`is_deleted` = '0' " \
            "AND `glpi_softwares`.`is_template` = '0' " \
            "ORDER BY  product, version"


def read_inventory():
    logger.info('GLPI - reading inventory')
    try:
        with closing(connect_to_mysql_server()) as connection:
            with connection.cursor() as cursor:
                cursor.execute(SQL_QUERY)
                return cursor.fetchall()
    except:
        logger.error('GLPI - unable to read inventory')
        logger.error('MYSQL - ' + str(traceback.format_exc()))
        raise


def connect_to_mysql_server():
    host = config.get_inventory_database_host()
    db_name = config.get_glpi_db_name()
    user = config.get_inventory_database_user()
    pwd = config.get_inventory_database_password()
    try:
        return pymysql.connect(host=host, user=user, password=pwd, db=db_name, cursorclass=pymysql.cursors.DictCursor)
    except Exception:
        logger.error('MYSQL - failed to connect to DB ' + db_name + ' in HOST ' + host + ' with USER ' + user)
        raise
