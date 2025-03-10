# Generated by Django 5.1.2 on 2024-12-13 10:49

import django.db.models.deletion
import tracker.models
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=50, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('client_type', models.CharField(blank=True, choices=[('BDA', 'Bilateral Donor Agency'), ('DB', 'Development Bank'), ('F', 'Foundation, Philanthropic'), ('GHI', 'Global Health Initiative'), ('O', 'Other')], max_length=3, null=True)),
            ],
            options={
                'db_table': 'client',
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('code', models.CharField(max_length=5, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name_plural': 'Countries',
                'db_table': 'country',
            },
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('code', models.CharField(max_length=3, primary_key=True, serialize=False)),
                ('currency', models.CharField(max_length=50)),
                ('symbol', models.CharField(blank=True, max_length=3, null=True)),
            ],
            options={
                'verbose_name_plural': 'currencies',
                'db_table': 'currency',
            },
        ),
        migrations.CreateModel(
            name='FundingAgency',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=50, unique=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name_plural': 'Funding Agencies',
                'db_table': 'funding_agency',
            },
        ),
        migrations.CreateModel(
            name='Institute',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=50, unique=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'institute',
            },
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=50, unique=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'unit',
            },
        ),
        migrations.CreateModel(
            name='Opportunity',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('ref_no', models.CharField(max_length=50, unique=True)),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('opp_type', models.CharField(choices=[('EOI', 'EOI'), ('RFP', 'RFP'), ('FC', 'Fore-cast')], max_length=3)),
                ('due_date', models.DateTimeField(blank=True, null=True)),
                ('clarification_date', models.DateTimeField(blank=True, null=True)),
                ('intent_bid_date', models.DateTimeField(blank=True, null=True)),
                ('duration_months', models.IntegerField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.IntegerField(choices=[(1, 'Entered'), (2, 'Go'), (3, 'NO-Go'), (4, 'Consider'), (5, 'Submitted'), (6, 'Lost'), (7, 'Won'), (8, 'Cancelled'), (9, 'Assumed Lost'), (10, 'N/A')], default=1)),
                ('submission_date', models.DateField(blank=True, null=True)),
                ('proposal_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('net_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('result_note', models.CharField(blank=True, max_length=300, null=True)),
                ('client', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Opportunities', to='tracker.client')),
                ('countries', models.ManyToManyField(related_name='Opportunities', to='tracker.country')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='created_opportunities', to=settings.AUTH_USER_MODEL)),
                ('currency', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Opportunities', to='tracker.currency')),
                ('funding_agency', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Opportunities', to='tracker.fundingagency')),
                ('lead_institute', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Opportunities', to='tracker.institute')),
                ('partners', models.ManyToManyField(related_name='partner_Opportunities', to='tracker.institute')),
                ('proposal_lead', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Opportunities', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('lead_unit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Opportunities', to='tracker.unit')),
            ],
            options={
                'db_table': 'opportunity',
            },
        ),
        migrations.CreateModel(
            name='OpportunityFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to=tracker.models.get_file_upload_path)),
                ('opportunity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Files', to='tracker.opportunity')),
            ],
            options={
                'db_table': 'opportunity_files',
            },
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=50, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(blank=True, max_length=255, null=True)),
                ('phone', models.CharField(blank=True, max_length=50, null=True)),
                ('unit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='tracker.unit')),
            ],
            options={
                'db_table': 'staff',
            },
        ),
    ]
