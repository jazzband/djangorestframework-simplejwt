from django.db import migrations, models


def is_vendor_less_than_mysql_innodb_56():
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute('SHOW VARIABLES LIKE "innodb_version"')

    mysql_version = cursor.fetchone()

    return mysql_version and mysql_version[1] < '5.7.0'


class Migration(migrations.Migration):
    dependencies = [
        ('token_blacklist', '0003_auto_20171017_2007'),
    ]

    operations = [
        migrations.AlterField(
            model_name='outstandingtoken',
            name='jti_hex',
            field=models.CharField(unique=True, max_length=191),
        )
        if is_vendor_less_than_mysql_innodb_56()
        else
        migrations.AlterField(
            model_name='outstandingtoken',
            name='jti_hex',
            field=models.CharField(unique=True, max_length=255),
        ),
    ]
