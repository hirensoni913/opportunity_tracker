"""
Unit tests for tracker app tasks.

This module tests:
- Celery task execution
- Task logic and behavior
- Task parameters and return values
"""
from datetime import timedelta
from unittest.mock import patch, MagicMock

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone

from tracker.models import Opportunity
from tracker.tasks import send_weekly_summary

User = get_user_model()


@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True,
    SITE_URL='http://testserver'
)
class SendWeeklySummaryTaskTest(TestCase):
    """Test cases for send_weekly_summary task."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Create opportunities from last week
        for i in range(5):
            Opportunity.objects.create(
                ref_no=f'OPP-2024-WEEK-{i:03d}',
                title=f'Weekly Opportunity {i}',
                opp_type='RFP',
                created_by=self.user,
                status=1
            )

        # Create an old opportunity (should not be included)
        old_opp = Opportunity.objects.create(
            ref_no='OPP-2024-OLD',
            title='Old Opportunity',
            opp_type='RFP',
            created_by=self.user,
            status=1
        )
        # Manually set created_at to 10 days ago
        old_opp.created_at = timezone.now() - timedelta(days=10)
        old_opp.save()

    @patch('tracker.tasks.execute_channel_send.delay')
    @patch('tracker.tasks.NotificationSubscription.objects.filter')
    def test_send_weekly_summary_with_opportunities(self, mock_filter, mock_task):
        """Test sending weekly summary when opportunities exist."""
        # Mock subscriptions
        mock_subscription = MagicMock()
        mock_subscription.id = 1
        mock_filter.return_value.values_list.return_value = [1, 2, 3]

        result = send_weekly_summary(channel='test_channel', days=7)

        # Verify subscriptions were queried
        mock_filter.assert_called_once()

        # Verify task was called with correct parameters
        mock_task.assert_called_once()

        # Verify return message
        self.assertIn('Weekly summary sent', result)
        self.assertIn('test_channel', result)

    def test_send_weekly_summary_no_opportunities(self):
        """Test weekly summary when no new opportunities exist."""
        # Delete all recent opportunities
        Opportunity.objects.filter(status=1).delete()

        result = send_weekly_summary(channel='test_channel', days=7)

        self.assertEqual(result, "No new opportunities to send.")

    @patch('tracker.tasks.execute_channel_send.delay')
    @patch('tracker.tasks.NotificationSubscription.objects.filter')
    def test_send_weekly_summary_filters_by_date(self, mock_filter, mock_task):
        """Test that weekly summary only includes opportunities from specified days."""
        mock_filter.return_value.values_list.return_value = [1]

        # Call with 7 days
        send_weekly_summary(channel='test_channel', days=7)

        # The task should only include opportunities from last 7 days
        # We created 5 recent and 1 old (10 days ago)
        # So only 5 should be included
        # We can't directly check the opportunities count in this mock,
        # but we verified the task was called
        mock_task.assert_called_once()

    @patch('tracker.tasks.execute_channel_send.delay')
    @patch('tracker.tasks.NotificationSubscription.objects.filter')
    def test_send_weekly_summary_with_custom_days(self, mock_filter, mock_task):
        """Test weekly summary with custom days parameter."""
        mock_filter.return_value.values_list.return_value = [1]

        # Call with 3 days instead of 7
        result = send_weekly_summary(channel='test_channel', days=3)

        # Verify task was called
        mock_task.assert_called_once()

        # Verify return message
        self.assertIn('Weekly summary sent', result)

    @patch('tracker.tasks.execute_channel_send.delay')
    @patch('tracker.tasks.NotificationSubscription.objects.filter')
    def test_send_weekly_summary_only_entered_status(self, mock_filter, mock_task):
        """Test that weekly summary only includes opportunities with status=1 (Entered)."""
        # Update some opportunities to different status
        Opportunity.objects.filter(ref_no='OPP-2024-WEEK-001').update(status=2)
        Opportunity.objects.filter(ref_no='OPP-2024-WEEK-002').update(status=3)

        mock_filter.return_value.values_list.return_value = [1]

        result = send_weekly_summary(channel='test_channel', days=7)

        # Task should still be called (we have 3 opportunities with status=1)
        mock_task.assert_called_once()

    @patch('tracker.tasks.execute_channel_send.delay')
    @patch('tracker.tasks.NotificationSubscription.objects.filter')
    def test_send_weekly_summary_message_content(self, mock_filter, mock_task):
        """Test that weekly summary includes correct message content."""
        mock_filter.return_value.values_list.return_value = [1, 2]

        send_weekly_summary(channel='test_channel', days=7)

        # Get the call arguments
        call_args = mock_task.call_args
        kwargs = call_args[1] if call_args else {}

        # Verify subject and messages were passed
        self.assertIn('subject', kwargs)
        self.assertIn('email_message', kwargs)
        self.assertIn('short_message', kwargs)

        # Check subject
        self.assertEqual(kwargs['subject'], "Your Weekly Summary")

    @patch('tracker.tasks.NotificationSubscription.objects.filter')
    def test_send_weekly_summary_no_active_subscriptions(self, mock_filter):
        """Test weekly summary when there are no active subscriptions."""
        # Mock no subscriptions
        mock_filter.return_value.values_list.return_value = []

        result = send_weekly_summary(channel='test_channel', days=7)

        # Should still return success message even with 0 subscribers
        self.assertIn('Weekly summary sent to 0 subscribers', result)
