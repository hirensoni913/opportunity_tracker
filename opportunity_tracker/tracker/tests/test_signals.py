"""
Unit tests for tracker app signals.

This module tests:
- Post-save signals for Opportunity model
- Notification triggers
- Signal behavior for create vs update
"""
from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from tracker.models import Opportunity
from tracker.signals import notify_new_opportunity

User = get_user_model()


class OpportunitySignalTest(TestCase):
    """Test cases for Opportunity post_save signal."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    @patch('tracker.signals._send_new_opportunity_notification')
    def test_signal_triggered_on_create(self, mock_send):
        """Test that signal is triggered when opportunity is created."""
        opportunity = Opportunity.objects.create(
            ref_no='OPP-2024-SIGNAL-1',
            title='Signal Test',
            opp_type='RFP',
            created_by=self.user,
            status=1
        )

        # Verify the notification function was called
        mock_send.assert_called_once()
        # Get the argument passed to the function
        call_args = mock_send.call_args[0]
        self.assertEqual(call_args[0].id, opportunity.id)

    @patch('tracker.signals._send_opportunity_update_notification')
    def test_signal_triggered_on_update(self, mock_send):
        """Test that signal is triggered when opportunity is updated."""
        opportunity = Opportunity.objects.create(
            ref_no='OPP-2024-SIGNAL-2',
            title='Signal Test Update',
            opp_type='RFP',
            created_by=self.user,
            status=1
        )

        # Reset mock to clear the create call
        mock_send.reset_mock()

        # Update the opportunity
        opportunity.title = 'Updated Title'
        opportunity.save()

        # Verify the update notification function was called
        mock_send.assert_called_once()

    @patch('tracker.signals._send_new_opportunity_notification')
    @patch('tracker.signals._send_opportunity_update_notification')
    def test_signal_only_create_notification_on_create(self, mock_update, mock_create):
        """Test that only create notification is sent on creation."""
        Opportunity.objects.create(
            ref_no='OPP-2024-SIGNAL-3',
            title='Signal Test',
            opp_type='RFP',
            created_by=self.user,
            status=1
        )

        mock_create.assert_called_once()
        mock_update.assert_not_called()

    @patch('tracker.signals._send_new_opportunity_notification')
    @patch('tracker.signals._send_opportunity_update_notification')
    def test_signal_only_update_notification_on_update(self, mock_update, mock_create):
        """Test that only update notification is sent on update."""
        opportunity = Opportunity.objects.create(
            ref_no='OPP-2024-SIGNAL-4',
            title='Signal Test',
            opp_type='RFP',
            created_by=self.user,
            status=1
        )

        # Reset mocks
        mock_create.reset_mock()
        mock_update.reset_mock()

        # Update
        opportunity.status = 2
        opportunity.save()

        mock_create.assert_not_called()
        mock_update.assert_called_once()


@override_settings(
    NEW_OPPORTUNITY_ALERT_CHANNEL='test_channel',
    SITE_URL='http://testserver'
)
class SendNewOpportunityNotificationTest(TestCase):
    """Test cases for _send_new_opportunity_notification function."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.opportunity = Opportunity.objects.create(
            ref_no='OPP-2024-NOTIF-1',
            title='Notification Test',
            opp_type='RFP',
            created_by=self.user,
            status=1
        )

    @patch('tracker.signals.execute_channel_send.delay')
    @patch('tracker.signals.NotificationChannel.objects.get')
    @patch('tracker.signals.NotificationSubscription.objects.filter')
    def test_send_new_opportunity_notification(self, mock_filter, mock_channel_get, mock_task):
        """Test sending new opportunity notification."""
        from tracker.signals import _send_new_opportunity_notification

        # Mock channel
        mock_channel = MagicMock()
        mock_channel_get.return_value = mock_channel

        # Mock subscriptions
        mock_subscription = MagicMock()
        mock_subscription.id = 1
        mock_filter.return_value.values_list.return_value = [1, 2, 3]

        result = _send_new_opportunity_notification(self.opportunity)

        # Verify NotificationChannel was queried
        mock_channel_get.assert_called_once()

        # Verify subscriptions were queried
        mock_filter.assert_called_once()

        # Verify task was called
        mock_task.assert_called_once()


@override_settings(SITE_URL='http://testserver')
class SendOpportunityUpdateNotificationTest(TestCase):
    """Test cases for _send_opportunity_update_notification function."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.opportunity = Opportunity.objects.create(
            ref_no='OPP-2024-NOTIF-2',
            title='Update Notification Test',
            opp_type='RFP',
            created_by=self.user,
            status=1
        )

    @patch('tracker.signals.execute_channel_send.delay')
    @patch('tracker.signals.OpportunitySubscription.objects.filter')
    def test_send_opportunity_update_notification(self, mock_filter, mock_task):
        """Test sending opportunity update notification."""
        from tracker.signals import _send_opportunity_update_notification

        # Mock subscriptions
        mock_filter.return_value.values_list.return_value = [1, 2]

        result = _send_opportunity_update_notification(self.opportunity)

        # Verify subscriptions were queried for this specific opportunity
        mock_filter.assert_called_once_with(
            opportunity=self.opportunity,
            is_active=True
        )

        # Verify task was called
        mock_task.assert_called_once()
