'''
Read-side listing serialization.

GET endpoints (lookup, paginate, recent, search, my listings) must return the
full category document — not a raw ``to_mongo()`` dump that drops ``id`` and
unset fields, and not the listsync card subset.
'''

from helpers.model_map import MODEL_MAP
from helpers.normalize import resolve_category
from listings.serializers import (
    ElectronicsSerializer,
    EventsSerializer,
    FashionSerializer,
    FurnitureSerializer,
    JobsSerializer,
    KidsSerializer,
    ListsyncSerializer,
    RealEstateSerializer,
    SavedItemSerializer,
    ServicesSerializer,
    SportsHobbySerializer,
    VehicleSerializer,
)

SERIALIZER_BY_CATEGORY = {
    'Vehicles': VehicleSerializer,
    'Services': ServicesSerializer,
    'realestate': RealEstateSerializer,
    'electronics': ElectronicsSerializer,
    'events': EventsSerializer,
    'jobs': JobsSerializer,
    'furniture': FurnitureSerializer,
    'fashion': FashionSerializer,
    'kids': KidsSerializer,
    'sportsandhobby': SportsHobbySerializer,
}


def serialize_listing(listing, request):
    '''Return the paginate-shaped dict for a category listing document.'''
    category = resolve_category(getattr(listing, 'category', None))
    serializer_cls = SERIALIZER_BY_CATEGORY.get(category)
    if serializer_cls is None:
        serializer_cls = SERIALIZER_BY_CATEGORY.get(
            getattr(listing, 'category', None)
        )
    if serializer_cls is None:
        data = listing.to_mongo().to_dict()
        data.pop('_id', None)
        if getattr(listing, 'id', None) is not None:
            data['id'] = str(listing.id)
            data['listing_id'] = str(listing.id)
        return data
    return serializer_cls(listing, context={'request': request}).data


def _docs_by_listing_id(rows, category_attr='category', id_attr='listing_id'):
    grouped = {}
    for row in rows:
        category = resolve_category(getattr(row, category_attr, None))
        listing_id = getattr(row, id_attr, None)
        if not category or listing_id is None or category not in MODEL_MAP:
            continue
        grouped.setdefault(category, []).append(listing_id)

    found = {}
    for category, ids in grouped.items():
        model = MODEL_MAP[category]
        for doc in model.objects.filter(id__in=ids):
            found[str(doc.id)] = doc
    return found


def serialize_listsync_rows(rows, request):
    '''Expand listsync card rows into full category listing payloads.'''
    docs = _docs_by_listing_id(rows)
    out = []
    for row in rows:
        doc = docs.get(str(getattr(row, 'listing_id', '')))
        if doc is not None:
            out.append(serialize_listing(doc, request))
            continue
        out.append(ListsyncSerializer(row, context={'request': request}).data)
    return out


def serialize_saved_rows(rows, request):
    '''Expand saved-item rows into full category listing payloads.'''
    docs = _docs_by_listing_id(rows)
    out = []
    for row in rows:
        doc = docs.get(str(getattr(row, 'listing_id', '')))
        if doc is not None:
            payload = dict(serialize_listing(doc, request))
            saved_at = getattr(row, 'saved_at', None)
            if saved_at is not None:
                payload['saved_at'] = saved_at.isoformat()
            out.append(payload)
            continue
        out.append(SavedItemSerializer(row, context={'request': request}).data)
    return out


class HydratedListsyncListMixin:
    '''Paginated listsync views that return full category documents.'''

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        rows = list(page) if page is not None else list(queryset)
        data = serialize_listsync_rows(rows, request)
        if page is not None:
            return self.get_paginated_response(data)
        from helpers import response
        from rest_framework import status

        return response(
            status=status.HTTP_200_OK,
            message='listings fetched Successfully',
            data=data,
        )
