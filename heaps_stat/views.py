from django.http import HttpResponseForbidden, HttpResponseNotFound, JsonResponse
from django.utils import timezone
from heaps_app.models import Celebrity, SocialNetwork
from heaps_stat import models


def social_link_clicks(request):
    if request.method == 'POST' and request.is_ajax():
        social_network_name = request.POST.get('social_network_name')
        slug = request.POST.get('slug')

        if social_network_name and slug:
            ip = request.META['REMOTE_ADDR']
            date = timezone.now().date()

            try:
                celebrity = Celebrity.objects.get(slug=slug)
                social_network = celebrity.socialnetwork_set.get(social_network=social_network_name)
            except (Celebrity.DoesNotExist, SocialNetwork.DoesNotExist):
                return HttpResponseNotFound("Not Found")

            try:
                stat_obj = models.SocialLinkClicks.objects.get(celebrity=celebrity, social_network=social_network)
            except models.SocialLinkClicks.DoesNotExist:
                stat_obj = models.SocialLinkClicks(celebrity=celebrity,
                                                   social_network=social_network.get_social_network_display(),
                                                   clicks_count=0)
                stat_obj.save()

            try:
                stat_obj.sociallinkclicksstat_set.get(ip=ip, date=date)
            except models.SocialLinkClicksStat.DoesNotExist:
                stat_obj.sociallinkclicksstat_set.create(ip=ip, date=date).save()
                stat_obj.clicks_count += 1
                stat_obj.save()

            return JsonResponse({
                'success': True,
            })

    return HttpResponseForbidden("Access denied")
