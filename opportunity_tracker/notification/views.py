import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.template.loader import render_to_string
from notification.models import OpportunitySubscription
from tracker.models import Opportunity


class ToggleSubscriptionView(View):
    def post(self, request, opportunity_id):
        # Get the opportunity instance
        opportunity = get_object_or_404(Opportunity, id=opportunity_id)

        try:
            # Parse the AJAX request body
            # data = json.loads(request.body)
            # is_subscribed = data.get('subscribe', False)
            is_subscribed = request.POST.get("is_subscribed") == "on"

            # Check if the user is subscribed
            subscription, created = OpportunitySubscription.objects.get_or_create(
                user=request.user, opportunity=opportunity)

            # Toggle subscription based on the checkbox
            subscription.is_active = is_subscribed
            subscription.save()

            # Redirect back to the opportunity update page
            return JsonResponse({'success': True, 'is_subscribed': subscription.is_active})
        except json.JSONDecodeError:
            print(request.body)
            return JsonResponse({'success': False, 'message': 'Invalid JSON Data'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)


def get_subscribers(request, opp_id):
    opportunity = get_object_or_404(Opportunity, id=opp_id)
    subscribers = OpportunitySubscription.objects.filter(
        opportunity=opportunity, is_active=True).select_related("user")
    html = render_to_string(
        "notification/subscribers_modal.html", {"subscribers": subscribers})
    return HttpResponse(html, {"subscribers": subscribers})
