# Generated by Django 5.2.2 on 2025-06-07 10:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='conversation',
            old_name='conversation_id',
            new_name='id',
        ),
        migrations.RenameField(
            model_name='message',
            old_name='message_id',
            new_name='id',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='user_id',
            new_name='id',
        ),
    ]
