from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scheduling", "0002_alter_crew_options_crew_hourly_rate_crew_trade_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="equipment",
            name="make",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="equipment",
            name="model",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="equipment",
            name="year",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]
