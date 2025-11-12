"""
Unit tests for tracker app models.

This module tests:
- Model creation and string representations
- Model properties and methods
- Model relationships (ForeignKey, ManyToMany)
- Model validation
- Custom model behavior
"""
from datetime import date, timedelta
from decimal import Decimal
import os
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.db.utils import IntegrityError

from tracker.models import (
    FundingAgency, Client, Institute, Unit, Staff, Country,
    Currency, Opportunity, OpportunityFile, get_file_upload_path
)

User = get_user_model()


class FundingAgencyModelTest(TestCase):
    """Test cases for FundingAgency model."""

    def setUp(self):
        """Set up test data."""
        self.agency = FundingAgency.objects.create(
            code="USAID",
            name="United States Agency for International Development"
        )

    def test_funding_agency_creation(self):
        """Test funding agency instance creation."""
        self.assertEqual(self.agency.code, "USAID")
        self.assertEqual(self.agency.name,
                         "United States Agency for International Development")
        self.assertIsInstance(self.agency.id, uuid.UUID)

    def test_funding_agency_str(self):
        """Test string representation of funding agency."""
        self.assertEqual(str(self.agency),
                         "United States Agency for International Development")

    def test_funding_agency_display_label(self):
        """Test display_label property."""
        expected = "USAID | United States Agency for International Development"
        self.assertEqual(self.agency.display_label, expected)

    def test_funding_agency_unique_code(self):
        """Test that code field is unique."""
        with self.assertRaises(IntegrityError):
            FundingAgency.objects.create(
                code="USAID",
                name="Another Agency"
            )

    def test_funding_agency_ordering(self):
        """Test default ordering by name."""
        agency2 = FundingAgency.objects.create(
            code="WHO", name="World Health Organization")
        agency3 = FundingAgency.objects.create(
            code="DFID", name="Department for International Development")

        agencies = list(FundingAgency.objects.all())
        self.assertEqual(agencies[0].code, "DFID")
        self.assertEqual(agencies[1].code, "USAID")
        self.assertEqual(agencies[2].code, "WHO")


class ClientModelTest(TestCase):
    """Test cases for Client model."""

    def setUp(self):
        """Set up test data."""
        self.client = Client.objects.create(
            code="GIZ",
            name="Deutsche Gesellschaft für Internationale Zusammenarbeit",
            client_type="BDA"
        )

    def test_client_creation(self):
        """Test client instance creation."""
        self.assertEqual(self.client.code, "GIZ")
        self.assertEqual(
            self.client.name, "Deutsche Gesellschaft für Internationale Zusammenarbeit")
        self.assertEqual(self.client.client_type, "BDA")

    def test_client_str(self):
        """Test string representation of client."""
        self.assertEqual(
            str(self.client), "Deutsche Gesellschaft für Internationale Zusammenarbeit")

    def test_client_display_label(self):
        """Test display_label property."""
        expected = "GIZ | Deutsche Gesellschaft für Internationale Zusammenarbeit"
        self.assertEqual(self.client.display_label, expected)

    def test_client_type_choices(self):
        """Test client type choices."""
        valid_types = ["BDA", "DB", "F", "GHI", "O"]
        for client_type in valid_types:
            client = Client.objects.create(
                code=f"TEST_{client_type}",
                name=f"Test {client_type}",
                client_type=client_type
            )
            self.assertEqual(client.client_type, client_type)

    def test_client_without_type(self):
        """Test client creation without type (optional field)."""
        client = Client.objects.create(code="TEST", name="Test Client")
        self.assertIsNone(client.client_type)


class InstituteModelTest(TestCase):
    """Test cases for Institute model."""

    def test_institute_creation(self):
        """Test institute instance creation."""
        institute = Institute.objects.create(
            code="MIT",
            name="Massachusetts Institute of Technology"
        )
        self.assertEqual(institute.code, "MIT")
        self.assertEqual(
            institute.name, "Massachusetts Institute of Technology")
        self.assertIsInstance(institute.id, uuid.UUID)


class UnitModelTest(TestCase):
    """Test cases for Unit model."""

    def test_unit_creation(self):
        """Test unit instance creation."""
        unit = Unit.objects.create(
            code="HR",
            name="Human Resources"
        )
        self.assertEqual(unit.code, "HR")
        self.assertEqual(unit.name, "Human Resources")


class StaffModelTest(TestCase):
    """Test cases for Staff model."""

    def setUp(self):
        """Set up test data."""
        self.unit = Unit.objects.create(
            code="IT", name="Information Technology")

    def test_staff_creation(self):
        """Test staff instance creation."""
        staff = Staff.objects.create(
            code="EMP001",
            name="John Doe",
            email="john.doe@example.com",
            phone="+1234567890",
            unit=self.unit
        )
        self.assertEqual(staff.code, "EMP001")
        self.assertEqual(staff.name, "John Doe")
        self.assertEqual(staff.email, "john.doe@example.com")
        self.assertEqual(staff.phone, "+1234567890")
        self.assertEqual(staff.unit, self.unit)

    def test_staff_str(self):
        """Test string representation of staff."""
        staff = Staff.objects.create(
            code="EMP001",
            name="Jane Smith",
            unit=self.unit
        )
        self.assertEqual(str(staff), "Jane Smith")

    def test_staff_without_unit(self):
        """Test staff creation without unit (optional field)."""
        staff = Staff.objects.create(
            code="EMP002",
            name="Bob Johnson"
        )
        self.assertIsNone(staff.unit)


class CountryModelTest(TestCase):
    """Test cases for Country model."""

    def test_country_creation(self):
        """Test country instance creation."""
        country, _ = Country.objects.get_or_create(
            code="US", defaults={"name": "United States"})
        self.assertEqual(country.code, "US")
        self.assertEqual(country.name, "United States")

    def test_country_str(self):
        """Test string representation of country."""
        country, _ = Country.objects.get_or_create(
            code="UK", defaults={"name": "United Kingdom"})
        self.assertEqual(str(country), "United Kingdom")

    def test_country_ordering(self):
        """Test default ordering by code."""
        Country.objects.get_or_create(code="ZW", defaults={"name": "Zimbabwe"})
        Country.objects.get_or_create(
            code="AF", defaults={"name": "Afghanistan"})
        Country.objects.get_or_create(code="BR", defaults={"name": "Brazil"})

        countries = list(Country.objects.filter(
            code__in=["ZW", "AF", "BR"]).order_by('code'))
        self.assertEqual(countries[0].code, "AF")
        self.assertEqual(countries[1].code, "BR")
        self.assertEqual(countries[2].code, "ZW")


class CurrencyModelTest(TestCase):
    """Test cases for Currency model."""

    def test_currency_creation(self):
        """Test currency instance creation."""
        currency, _ = Currency.objects.get_or_create(
            code="USD",
            defaults={"currency": "US Dollar", "symbol": "$"}
        )
        self.assertEqual(currency.code, "USD")
        self.assertEqual(currency.currency, "US Dollar")
        self.assertEqual(currency.symbol, "$")

    def test_currency_str(self):
        """Test string representation of currency."""
        currency, _ = Currency.objects.get_or_create(
            code="EUR", defaults={"currency": "Euro", "symbol": "€"})
        self.assertEqual(str(currency), "EUR")


class OpportunityModelTest(TestCase):
    """Test cases for Opportunity model."""

    def setUp(self):
        """Set up test data for opportunities."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
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
        self.unit = Unit.objects.create(
            code="IT", name="Information Technology")
        self.institute = Institute.objects.create(
            code="MIT", name="Massachusetts Institute of Technology")

    def test_opportunity_creation(self):
        """Test opportunity instance creation."""
        opportunity = Opportunity.objects.create(
            ref_no="OPP-2024-001",
            title="Test Opportunity",
            funding_agency=self.funding_agency,
            client=self.client,
            opp_type="RFP",
            due_date=date.today() + timedelta(days=30),
            created_by=self.user,
            status=1
        )

        self.assertEqual(opportunity.ref_no, "OPP-2024-001")
        self.assertEqual(opportunity.title, "Test Opportunity")
        self.assertEqual(opportunity.opp_type, "RFP")
        self.assertEqual(opportunity.status, 1)
        self.assertIsInstance(opportunity.id, uuid.UUID)

    def test_opportunity_str(self):
        """Test string representation of opportunity."""
        opportunity = Opportunity.objects.create(
            ref_no="OPP-2024-002",
            title="Another Opportunity",
            opp_type="EOI",
            created_by=self.user
        )
        self.assertEqual(str(opportunity), "OPP-2024-002")

    def test_opportunity_unique_ref_no(self):
        """Test that ref_no field is unique."""
        Opportunity.objects.create(
            ref_no="OPP-2024-003",
            title="First Opportunity",
            opp_type="RFP",
            created_by=self.user
        )

        with self.assertRaises(IntegrityError):
            Opportunity.objects.create(
                ref_no="OPP-2024-003",
                title="Duplicate Opportunity",
                opp_type="EOI",
                created_by=self.user
            )

    def test_opportunity_with_many_to_many_countries(self):
        """Test opportunity with multiple countries."""
        opportunity = Opportunity.objects.create(
            ref_no="OPP-2024-004",
            title="Multi-country Opportunity",
            opp_type="RFP",
            created_by=self.user
        )

        country2, _ = Country.objects.get_or_create(
            code="TZ", defaults={"name": "Tanzania"})
        opportunity.countries.add(self.country, country2)

        self.assertEqual(opportunity.countries.count(), 2)
        self.assertIn(self.country, opportunity.countries.all())
        self.assertIn(country2, opportunity.countries.all())

    def test_opportunity_status_display(self):
        """Test get_status_display method."""
        opportunity = Opportunity.objects.create(
            ref_no="OPP-2024-005",
            title="Status Test",
            opp_type="RFP",
            created_by=self.user,
            status=2
        )
        self.assertEqual(opportunity.get_status_display(), "Go")

        opportunity.status = 11
        opportunity.save()
        self.assertEqual(opportunity.get_status_display(),
                         "Transferred to RFP")

    def test_opportunity_submission_expiry(self):
        """Test submission_expiry property calculation."""
        opportunity = Opportunity.objects.create(
            ref_no="OPP-2024-006",
            title="Expiry Test",
            opp_type="RFP",
            created_by=self.user,
            submission_date=date(2024, 1, 1),
            submission_validity=30
        )

        expected_expiry = date(2024, 1, 1) + timedelta(days=30)
        self.assertEqual(opportunity.submission_expiry, expected_expiry)

    def test_opportunity_submission_expiry_without_data(self):
        """Test submission_expiry returns None when data is missing."""
        opportunity = Opportunity.objects.create(
            ref_no="OPP-2024-007",
            title="No Expiry",
            opp_type="RFP",
            created_by=self.user
        )
        self.assertIsNone(opportunity.submission_expiry)

    def test_opportunity_with_parent(self):
        """Test opportunity transfer relationship (parent-child)."""
        parent = Opportunity.objects.create(
            ref_no="EOI-2024-001",
            title="Parent EOI",
            opp_type="EOI",
            created_by=self.user,
            status=11  # Transferred to RFP
        )

        child = Opportunity.objects.create(
            ref_no="RFP-2024-001",
            title="Child RFP",
            opp_type="RFP",
            created_by=self.user,
            parent=parent
        )

        self.assertEqual(child.parent, parent)
        self.assertEqual(parent.transferred.first(), child)

    def test_get_transferred_opportunity(self):
        """Test get_transferred_opportunity method."""
        parent = Opportunity.objects.create(
            ref_no="EOI-2024-002",
            title="Parent EOI 2",
            opp_type="EOI",
            created_by=self.user,
            status=11
        )

        child = Opportunity.objects.create(
            ref_no="RFP-2024-002",
            title="Child RFP 2",
            opp_type="RFP",
            created_by=self.user,
            parent=parent
        )

        self.assertEqual(parent.get_transferred_opportunity(), child)

        # Test when status is not 11
        parent.status = 1
        parent.save()
        self.assertIsNone(parent.get_transferred_opportunity())

    def test_opportunity_with_decimal_fields(self):
        """Test opportunity with proposal_amount and net_amount."""
        opportunity = Opportunity.objects.create(
            ref_no="OPP-2024-008",
            title="Budget Test",
            opp_type="RFP",
            created_by=self.user,
            currency=self.currency,
            proposal_amount=Decimal("1000000.50"),
            net_amount=Decimal("950000.25")
        )

        self.assertEqual(opportunity.proposal_amount, Decimal("1000000.50"))
        self.assertEqual(opportunity.net_amount, Decimal("950000.25"))

    def test_opportunity_relationships(self):
        """Test all foreign key relationships."""
        opportunity = Opportunity.objects.create(
            ref_no="OPP-2024-009",
            title="Relationship Test",
            opp_type="RFP",
            created_by=self.user,
            funding_agency=self.funding_agency,
            client=self.client,
            currency=self.currency,
            lead_unit=self.unit,
            proposal_lead=self.user,
            lead_institute=self.institute
        )

        self.assertEqual(opportunity.funding_agency, self.funding_agency)
        self.assertEqual(opportunity.client, self.client)
        self.assertEqual(opportunity.currency, self.currency)
        self.assertEqual(opportunity.lead_unit, self.unit)
        self.assertEqual(opportunity.proposal_lead, self.user)
        self.assertEqual(opportunity.lead_institute, self.institute)


@override_settings(MEDIA_ROOT='/tmp/test_media/')
class OpportunityFileModelTest(TestCase):
    """Test cases for OpportunityFile model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.opportunity = Opportunity.objects.create(
            ref_no="OPP-2024-010",
            title="File Test Opportunity",
            opp_type="RFP",
            created_by=self.user
        )

    def test_get_file_upload_path(self):
        """Test file upload path generation."""
        # Create a mock file instance
        mock_file = SimpleUploadedFile("test.pdf", b"file_content")
        opp_file = OpportunityFile(
            opportunity=self.opportunity, file=mock_file)

        # Test the path generation
        path = get_file_upload_path(opp_file, "test.pdf")
        expected_prefix = "opportunities/OPP_2024_010/"

        self.assertTrue(path.startswith(expected_prefix))
        self.assertTrue(path.endswith("test.pdf"))

    def test_opportunity_file_creation(self):
        """Test opportunity file instance creation."""
        mock_file = SimpleUploadedFile("document.pdf", b"file_content")
        opp_file = OpportunityFile.objects.create(
            opportunity=self.opportunity,
            file=mock_file
        )

        self.assertEqual(opp_file.opportunity, self.opportunity)
        self.assertTrue(opp_file.file.name.startswith(
            "opportunities/OPP_2024_010/"))

    def test_opportunity_file_relationship(self):
        """Test reverse relationship from Opportunity to OpportunityFile."""
        mock_file1 = SimpleUploadedFile("doc1.pdf", b"content1")
        mock_file2 = SimpleUploadedFile("doc2.pdf", b"content2")

        OpportunityFile.objects.create(
            opportunity=self.opportunity, file=mock_file1)
        OpportunityFile.objects.create(
            opportunity=self.opportunity, file=mock_file2)

        self.assertEqual(self.opportunity.Files.count(), 2)

    def tearDown(self):
        """Clean up test files."""
        # Clean up any created files
        import shutil
        test_media_root = '/tmp/test_media/'
        if os.path.exists(test_media_root):
            shutil.rmtree(test_media_root)
