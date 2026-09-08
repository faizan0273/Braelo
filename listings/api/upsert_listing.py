'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
Populate Listing and save listings endpoints.
---------------------------------------------------
'''

from rest_framework import status
from rest_framework_mongoengine import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from helpers.notifications import listing_created_event
from notifications.serializers.events import EventNotificationSerializer


from listings.models import (
    ElectronicsListing,
    EventsListing,
    FashionListing,
    JobsListing,
    ServicesListing,
    SportsHobbyListing,
    KidsListing,
    FurnitureListing,
    RealEstateListing,
    VehicleListing,
)
from helpers import response, handle_exceptions
from listings.field_contract import (
    apply_field_aliases,
    coerce_optional_int_fields,
    extract_coordinates,
)
from listings.serializers import (
    RealEstateSerializer,
    ElectronicsSerializer,
    EventsSerializer,
    FurnitureSerializer,
    FashionSerializer,
    JobsSerializer,
    ServicesSerializer,
    SportsHobbySerializer,
    KidsSerializer,
    VehicleSerializer,
)


def _normalize_keywords(raw):
    '''
    Build a list[str] for ListField(StringField): split comma-separated text,
    strip accidental wrapping quotes (e.g. 'abc' from Postman), coerce non-strings.

    Multipart often sends one field value like "abc, used" → getlist may yield
    one string; we split commas inside each segment too.
    '''
    if raw is None:
        return []

    def _unwrap_token(s):
        s = str(s).strip()
        if s.startswith('[') and s.endswith(']') and ',' in s:
            s = s[1:-1].strip()
        if (s.startswith("'") and s.endswith("'")) or (
            s.startswith('"') and s.endswith('"')
        ):
            s = s[1:-1].strip()
        return s.strip('[]').strip()

    parts = []
    if isinstance(raw, (list, tuple)):
        for item in raw:
            s = _unwrap_token(item)
            if not s:
                continue
            if ',' in s:
                parts.extend([_unwrap_token(x) for x in s.split(',') if _unwrap_token(x)])
            else:
                parts.append(s)
    else:
        text = _unwrap_token(raw)
        if not text:
            return []
        parts = [_unwrap_token(s) for s in text.split(',') if _unwrap_token(s)]
    out = []
    for p in parts:
        s = _unwrap_token(p)
        if s:
            out.append(s)
    return out


def _listing_create_payload(request, listing_coordinates):
    '''
    Plain dict for DRF/mongo ListField: QueryDict + ListField mixes getlist()
    with indexed keys (keywords[0]) and breaks CharField children. Files stay
    on getlist('pictures').
    '''
    qd = request.data
    payload = {}
    for key in qd.keys():
        if key in ('pictures', 'keywords', 'listing_coordinates'):
            continue
        payload[key] = qd.get(key)
    payload.pop('access_token', None)
    payload['listing_coordinates'] = listing_coordinates
    file_list = request.FILES.getlist('pictures')
    if file_list:
        payload['pictures'] = file_list
    fb = payload.get('from_business')
    if isinstance(fb, str):
        payload['from_business'] = fb.strip().lower() in (
            'true',
            '1',
            'yes',
        )
    if hasattr(qd, 'getlist'):
        kw_list = qd.getlist('keywords')
        if len(kw_list) > 1:
            raw_kw = kw_list
        elif len(kw_list) == 1:
            raw_kw = kw_list[0]
        else:
            raw_kw = qd.get('keywords')
    else:
        raw_kw = qd.get('keywords')
    payload['keywords'] = _normalize_keywords(raw_kw)
    payload = apply_field_aliases(
        payload, subcategory=payload.get('subcategory')
    )
    return coerce_optional_int_fields(payload)


class Listing(generics.CreateAPIView):
    '''
    Base API endpoint to create a new listing for different categories.
    '''

    permission_classes = [IsAuthenticated]

    def send_notification(self, serializer):
        try:
            listing_id = serializer.data['id']
            category = serializer.data['category']
            user_id = serializer.data['user_id']
            event_serializer = EventNotificationSerializer(
                data=listing_created_event(user_id, listing_id, category)
            )
            event_serializer.is_valid(raise_exception=True)
            event_serializer.save()
            from notifications.services.email import email_service
            from notifications.services.preferences import is_preference_enabled
            from users.models import User

            if is_preference_enabled(user_id, 'listing_created'):
                owner = User.objects.filter(id=user_id).first()
                if owner and owner.email:
                    email_service.send_best_effort(
                        to=owner.email,
                        template_key='listing_created',
                        context={
                            'name': owner.name or owner.first_name or '',
                            'listing_title': serializer.data.get('title') or '',
                            'category': category,
                        },
                    )
        except Exception:
            pass

    @handle_exceptions
    def post(self, request, **kwargs):
        '''
        POST method to add a listing.
        :param request: request object. (dict)
        :return: listing status. (json)
        '''
        listing_coordinates = request.data.get('listing_coordinates')
        if not listing_coordinates:
            raise ValidationError(
                {'listing_coordinates': 'field is required'}
            )
        listing_coordinates = extract_coordinates(listing_coordinates)
        if listing_coordinates is None:
            raise ValidationError(
                {
                    'listing_coordinates': (
                        'listing_coordinates must be a list with [longitude, latitude].'
                    )
                }
            )
        payload = _listing_create_payload(request, listing_coordinates)
        serializer = self.get_serializer(
            data=payload, context={'request': request}
        )
        # Validate and create the listing if valid
        serializer.is_valid(raise_exception=True)
        serializer.save()
        self.send_notification(serializer)

        return response(
            status=status.HTTP_201_CREATED,
            message='Listing created successfully',
            data=serializer.data,
        )


class VehicleAPI(Listing):
    '''
    API endpoint to create a new vehicle listings.
    '''

    serializer_class = VehicleSerializer

    def get_queryset(self):
        return VehicleListing.objects.all()


class RealEstateAPI(Listing):
    '''
    API endpoint to create a new vehicle listings.
    '''

    serializer_class = RealEstateSerializer

    def get_queryset(self):
        return RealEstateListing.objects.all()


class ElectronicsAPI(Listing):
    '''
    API endpoint to create a new vehicle listings.
    '''

    serializer_class = ElectronicsSerializer

    def get_queryset(self):
        return ElectronicsListing.objects.all()


class EventsAPI(Listing):
    '''
    API endpoint to create a new vehicle listings.
    '''

    serializer_class = EventsSerializer

    def get_queryset(self):
        return EventsListing.objects.all()


class FashionAPI(Listing):
    '''
    API endpoint to create a new vehicle listings.
    '''

    serializer_class = FashionSerializer

    def get_queryset(self):
        return FashionListing.objects.all()


class JobsAPI(Listing):
    '''
    API endpoint to create a new vehicle listings.
    '''

    serializer_class = JobsSerializer

    def get_queryset(self):
        return JobsListing.objects.all()


class ServicesAPI(Listing):
    '''
    API endpoint to create service-class listings (ServicesListing).
    '''

    serializer_class = ServicesSerializer

    def get_queryset(self):
        return ServicesListing.objects.all()


class SportsHobbyAPI(Listing):
    '''
    API endpoint to create a new vehicle listings.
    '''

    serializer_class = SportsHobbySerializer

    def get_queryset(self):
        return SportsHobbyListing.objects.all()


class KidsAPI(Listing):
    '''
    API endpoint to create a new vehicle listings.
    '''

    serializer_class = KidsSerializer

    def get_queryset(self):
        return KidsListing.objects.all()


class FurnitureAPI(Listing):
    '''
    API endpoint to create a new vehicle listings.
    '''

    serializer_class = FurnitureSerializer

    def get_queryset(self):
        return FurnitureListing.objects.all()
