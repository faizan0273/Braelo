'''Shared delete helpers for listings (Mongo) and users (SQL + Mongo).'''

from __future__ import annotations

from admin_panel.models import AdminBusinessBanner
from helpers.model_map import MODEL_MAP
from helpers.models.listsync import ListSync
from listings.models.saved_listing import SavedItem
from users.models import (
    Business,
    BusinessAnalyticsEvent,
    Interest,
    User,
    UserDeviceToken,
)
from users.models.business_settings import BusinessSettings, SavedReply
from users.services.listings_directory_sync import (
    LISTING_MARKER_BY_COLLECTION,
    listing_source_for_model,
    remove_listing_directory_doc,
)


def resolve_users(*, emails=None, user_ids=None, include_staff=False):
    qs = User.objects.all()
    emails = [e.strip().lower() for e in (emails or []) if e and e.strip()]
    ids = [int(i) for i in (user_ids or [])]
    if emails:
        qs = qs.filter(email__in=emails) | qs.filter(username__in=emails)
    if ids:
        qs = qs.filter(id__in=ids)
    if not include_staff:
        qs = qs.filter(is_staff=False, is_superuser=False)
    return list(qs.distinct())


def listing_counts(user_ids=None):
    counts = {}
    for name, model in MODEL_MAP.items():
        qs = model.objects
        if user_ids is not None:
            qs = qs.filter(user_id__in=user_ids)
        counts[name] = qs.count()
    sync_qs = ListSync.objects
    saved_qs = SavedItem.objects
    if user_ids is not None:
        sync_qs = sync_qs.filter(user_id__in=user_ids)
        saved_qs = saved_qs.filter(user_id__in=user_ids)
    counts['listsync'] = sync_qs.count()
    counts['saved_listings'] = saved_qs.count()
    return counts


def delete_listings(*, user_ids=None, dry_run=True):
    """Delete category listings, listsync, saved rows, and directory mirrors."""
    summary = listing_counts(user_ids)
    if dry_run:
        return summary

    for _name, model in MODEL_MAP.items():
        qs = model.objects
        if user_ids is not None:
            qs = qs.filter(user_id__in=user_ids)
        source = listing_source_for_model(model)
        for listing in qs.only('id'):
            remove_listing_directory_doc(str(listing.id), source)
        qs.delete()

    sync_qs = ListSync.objects
    saved_qs = SavedItem.objects
    if user_ids is not None:
        sync_qs = sync_qs.filter(user_id__in=user_ids)
        saved_qs = saved_qs.filter(user_id__in=user_ids)
        User.objects.filter(id__in=user_ids).update(listings_count=0)
    else:
        _purge_all_listing_mirrors()
        User.objects.update(listings_count=0)
    sync_qs.delete()
    saved_qs.delete()
    return summary


def _purge_all_listing_mirrors():
    try:
        from chatbot.mongo_db import get_db

        get_db()['businesses'].delete_many(
            {'listing_source': {'$in': list(LISTING_MARKER_BY_COLLECTION)}}
        )
    except Exception:
        pass


def delete_mongo_for_users(user_ids):
    if not user_ids:
        return
    Interest.objects.filter(user_id__in=user_ids).delete()
    UserDeviceToken.objects.filter(user_id__in=user_ids).delete()
    Business.objects.filter(user_id__in=user_ids).delete()
    BusinessSettings.objects.filter(user_id__in=user_ids).delete()
    SavedReply.objects.filter(user_id__in=user_ids).delete()
    BusinessAnalyticsEvent.objects.filter(user_id__in=user_ids).delete()
    AdminBusinessBanner.objects.filter(user_id__in=user_ids).delete()


def delete_users(*, users, dry_run=True):
    user_ids = [u.id for u in users]
    listing_summary = delete_listings(user_ids=user_ids, dry_run=dry_run)
    if dry_run:
        return listing_summary
    delete_mongo_for_users(user_ids)
    deleted, _ = User.objects.filter(id__in=user_ids).delete()
    listing_summary['sql_users'] = deleted
    return listing_summary
