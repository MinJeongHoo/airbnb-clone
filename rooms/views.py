from django.utils import timezone
from django.views.generic import ListView, DetailView, View
from django.shortcuts import render
from django_countries import countries
from django.core.paginator import Paginator
from . import models, forms


class HomeView(ListView):
    """HomewView Definition"""

    model = models.Room
    paginate_by = 12
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


# def roomSearch(request):
#     city = request.GET.get("city", "Anywhere")
#     country = request.GET.get("country", "KR")
#     room_type = int(request.GET.get("room_type", 0))
#     room_types = models.RoomType.objects.all()
#     price = int(request.GET.get("price", 0))
#     guests = int(request.GET.get("guests", 0))
#     bedrooms = int(request.GET.get("bedrooms", 0))
#     baths = int(request.GET.get("bedroomsbaths", 0))
#     instant = bool(request.GET.get("instant", False))
#     superhost = bool(request.GET.get("superhost", False))
#     s_amenities = request.GET.getlist("amenities")
#     s_facilities = request.GET.getlist("facilities")

#     form = {
#         "city": city,
#         "s_country": country,
#         "s_room_type": room_type,
#         "price": price,
#         "guests": guests,
#         "bedrooms": bedrooms,
#         "baths": baths,
#         "s_amenities": s_amenities,
#         "s_facilities": s_facilities,
#         "superhost": superhost,
#         "instant": instant,
#     }

#     amenities = models.Amenity.objects.all()
#     facilities = models.Facility.objects.all()

#     choices = {
#         "countries": countries,
#         "room_types": room_types,
#         "amenities": amenities,
#         "facilities": facilities,
#     }

#     filter_args = {}

#     if city != "Anywhere":
#         filter_args["city__startswith"] = city
#     filter_args["country"] = country

#     if room_type != 0:
#         filter_args["room_type__pk"] = room_type
#     if price != 0:
#         filter_args["price__lte"] = price
#     if guests != 0:
#         filter_args["guests_lte"] = guests
#     if bedrooms != 0:
#         filter_args["bedrooms_lte"] = bedrooms
#     if baths != 0:
#         filter_args["baths_lte"] = baths
#     if instant is True:
#         filter_args["instant_book"] = True
#     if superhost is True:
#         filter_args["host__superhost"] = True

#     if len(s_amenities) > 0:
#         for s_amenity in s_amenities:
#             filter_args["amenities__pk"] = int(s_amenity)
#     if len(s_facilities) > 0:
#         for s_facilitiy in s_facilities:
#             filter_args["facilities__pk"] = int(s_facilitiy)
#     rooms = models.Room.objects.filter(**filter_args)
#     return render(request, "rooms/search.html", {**form, **choices, "rooms": rooms})


class SearchView(View):
    def get(self, request):

        country = request.GET.get("country")

        if country:
            ##request.GET하면 form정보를 기억
            form = forms.SearchForm(request.GET)
            if form.is_valid():
                city = form.cleaned_data.get("city")
                country = form.cleaned_data.get("country")
                price = form.cleaned_data.get("price")
                room_type = form.cleaned_data.get("room_type")
                price = form.cleaned_data.get("price")
                guests = form.cleaned_data.get("guests")
                bedrooms = form.cleaned_data.get("bedrooms")
                beds = form.cleaned_data.get("beds")
                baths = form.cleaned_data.get("baths")
                instant_book = form.cleaned_data.get("instant_book")
                superhost = form.cleaned_data.get("superhost")
                amenities = form.cleaned_data.get("amenities")
                facilities = form.cleaned_data.get("facilities")

                ##검색 filter
                filter_args = {}
                if city != "Anywhere":
                    filter_args["city__startswith"] = city

                filter_args["country"] = country

                if room_type is not None:
                    filter_args["room_type__pk"] = room_type
                if price is not None:
                    filter_args["price__lte"] = price
                if guests is not None:
                    filter_args["guests__lte"] = guests
                if beds is not None:
                    filter_args["bedrooms__lte"] = bedrooms
                if baths is not None:
                    filter_args["baths__lte"] = baths
                if instant_book is True:
                    filter_args["instant_book"] = True
                if superhost is True:
                    filter_args["host__superhost"] = True

                for amenity in amenities:
                    filter_args["amenities"] = amenity

                for facilitiy in facilities:
                    filter_args["facilities"] = facilitiy
                qs = models.Room.objects.filter(**filter_args)
                paginator = Paginator(qs, 10, orphans=5)
                page = request.GET.get("page", 1)
                rooms = paginator.get_page(page)
                return render(
                    request, "rooms/search.html", {"form": form, "rooms": rooms}
                )

        else:
            form = forms.SearchForm()
        return render(request, "rooms/search.html", {"form": form})
