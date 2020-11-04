from django.utils import timezone
from django.views.generic import ListView, DetailView
from django.shortcuts import render
from django_countries import countries
from . import models


class HomeView(ListView):
    """HomewView Definition"""

    model = models.Room
    paginate_by = 10
    paginate_orphans = 5
    ordering = "created"
    """object list name 변경"""
    context_object_name = "rooms"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        context["now"] = now
        return context


class RoomDetail(DetailView):

    """ RoomDetail Definitaion"""

    model = models.Room


def roomSearch(request):
    city = request.GET.get("city", "Anywhere")
    country = request.GET.get("country", "KR")
    room_type = int(request.GET.get("room_type", 0))
    room_types = models.RoomType.objects.all()
    price = int(request.GET.get("price", 0))
    guests = int(request.GET.get("guests", 0))
    bedrooms = int(request.GET.get("bedrooms", 0))
    baths = int(request.GET.get("bedroomsbaths", 0))
    s_amenities = request.GET.getlist("amenities")
    s_facilities = request.GET.getlist("facilities")

    print(s_amenities, s_facilities)

    form = {
        "city": city,
        "s_country": country,
        "s_room_type": room_type,
        "price": price,
        "guests": guests,
        "bedrooms": bedrooms,
        "baths": baths,
        "s_amenities": s_amenities,
        "s_facilities": s_facilities,
    }

    amenities = models.Amenity.objects.all()
    facilities = models.Facility.objects.all()

    choices = {
        "countries": countries,
        "room_types": room_types,
        "amenities": amenities,
        "facilities": facilities,
    }
    return render(request, "rooms/search.html", {**form, **choices})
