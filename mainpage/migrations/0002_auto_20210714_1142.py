# Generated by Django 3.1.1 on 2021-07-14 11:42

from django.db import migrations, models
import mainpage.utils
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('mainpage', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='banner',
            name='link',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='banner',
            name='image',
            field=sorl.thumbnail.fields.ImageField(max_length=255, null=True, upload_to=mainpage.utils.get_banner_upload_path),
        ),
    ]