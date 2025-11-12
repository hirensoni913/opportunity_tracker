"""
Unit tests for tracker app serializers.

This module tests:
- Serializer field validation
- Serializer data representation
- Read-only fields
- Custom create/update methods
"""
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from tracker.models import (
    FundingAgency, Client, Country, Currency, Opportunity
)
from tracker.serializers import OpportunitySerializer

User = get_user_model()


class OpportunitySerializerTest(TestCase):
    """Test cases for OpportunitySerializer."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.funding_agency = FundingAgency.objects.create(
            code="USAID",
            name="United States Agency for International Development"
        )
        self.client = Client.objects.create(
            code="GIZ",
            name="Deutsche Gesellschaft für Internationale Zusammenarbeit"
        )
        self.country, _ = Country.objects.get_or_create(
            code="KE", defaults={"name": "Kenya"})
        self.currency, _ = Currency.objects.get_or_create(
            code="USD", defaults={"currency": "US Dollar", "symbol": "$"})

        self.opportunity = Opportunity.objects.create(
            ref_no='OPP-2024-SER-1',
            title='Serializer Test',
            funding_agency=self.funding_agency,
            client=self.client,
            opp_type='RFP',
            due_date=date.today() + timedelta(days=30),
            created_by=self.user,
            status=1
        )
        self.opportunity.countries.add(self.country)

        self.factory = APIRequestFactory()

    def test_opportunity_serializer_fields(self):
        """Test that serializer includes all expected fields."""
        serializer = OpportunitySerializer(instance=self.opportunity)
        data = serializer.data

        # Check key fields are present
        self.assertIn('id', data)
        self.assertIn('ref_no', data)
        self.assertIn('title', data)
        self.assertIn('funding_agency', data)
        self.assertIn('client', data)
        self.assertIn('opp_type', data)
        self.assertIn('status', data)
        self.assertIn('created_by', data)
        self.assertIn('created_at', data)

    def test_opportunity_serializer_read_only_fields(self):
        """Test that read-only fields cannot be modified."""
        serializer = OpportunitySerializer(instance=self.opportunity)

        # Check read-only fields
        self.assertIn('id', serializer.Meta.read_only_fields)
        self.assertIn('created_by', serializer.Meta.read_only_fields)
        self.assertIn('created_at', serializer.Meta.read_only_fields)
        self.assertIn('updated_by', serializer.Meta.read_only_fields)
        self.assertIn('updated_at', serializer.Meta.read_only_fields)

    def test_opportunity_serializer_create(self):
        """Test creating opportunity through serializer."""
        data = {
            'ref_no': 'OPP-2024-SER-2',
            'title': 'New Serializer Test',
            'opp_type': 'EOI',
            'status': 1,
            'countries': [self.country.code],  # Use country code (primary key)
        }

        # Create a mock request with user
        request = self.factory.post('/api/Opportunity/')
        request.user = self.user

        serializer = OpportunitySerializer(
            data=data, context={'request': request})
        self.assertTrue(serializer.is_valid(), serializer.errors)

        opportunity = serializer.save()

        self.assertEqual(opportunity.ref_no, 'OPP-2024-SER-2')
        self.assertEqual(opportunity.created_by, self.user)

    def test_opportunity_serializer_validation(self):
        """Test serializer validation."""
        # Missing required fields
        data = {
            'title': 'Invalid Opportunity',
        }

        request = self.factory.post('/api/Opportunity/')
        request.user = self.user

        serializer = OpportunitySerializer(
            data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('ref_no', serializer.errors)
        self.assertIn('opp_type', serializer.errors)

    def test_opportunity_serializer_update(self):
        """Test updating opportunity through serializer."""
        data = {
            'ref_no': 'OPP-2024-SER-1',
            'title': 'Updated Serializer Test',
            'opp_type': 'RFP',
            'status': 2,
            'countries': [self.country.code],  # Use country code (primary key)
        }

        request = self.factory.put(f'/api/Opportunity/{self.opportunity.id}/')
        request.user = self.user

        serializer = OpportunitySerializer(
            instance=self.opportunity,
            data=data,
            context={'request': request}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

        opportunity = serializer.save()

        self.assertEqual(opportunity.title, 'Updated Serializer Test')
        self.assertEqual(opportunity.status, 2)

    def test_opportunity_serializer_with_relationships(self):
        """Test serializer with foreign key relationships."""
        serializer = OpportunitySerializer(instance=self.opportunity)
        data = serializer.data

        self.assertEqual(str(data['funding_agency']),
                         str(self.funding_agency.id))
        self.assertEqual(str(data['client']), str(self.client.id))
        self.assertIn(self.country.code, data['countries'])

    def test_opportunity_serializer_all_fields(self):
        """Test that serializer uses all model fields."""
        serializer = OpportunitySerializer()
        self.assertEqual(serializer.Meta.fields, "__all__")
