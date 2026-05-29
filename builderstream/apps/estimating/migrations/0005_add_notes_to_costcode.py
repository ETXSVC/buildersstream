from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("estimating", "0004_proposal_client_set_null"),
    ]

    operations = [
        migrations.AddField(
            model_name="costcode",
            name="notes",
            field=models.TextField(blank=True),
        ),
    ]
