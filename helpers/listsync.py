'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
Listing synchronization with listsync collection helper class.
---------------------------------------------------
'''

from mongoengine import DoesNotExist, OperationError
from rest_framework.exceptions import ValidationError


class ListSynchronize:
    '''
    List synchronization helper class.
    '''

    @staticmethod
    def flip_status(listing_id, status, user_id, model=None):
        '''
        flip status for certain list.
        '''
        from helpers import ListSync

        model = model or ListSync
        filter_by = 'listing_id' if model == ListSync else 'id'

        try:
            filter_by = 'listing_id' if model == ListSync else 'id'
            active_status = model.objects(
                **{filter_by: listing_id, 'user_id': user_id}
            ).first()

            # if category or user_id or listing _id is not correct=
            active_status = model.objects(**{filter_by: listing_id}).first()
            # if category or listing _id is not correct)
            if not active_status:
                raise ValidationError({'Listings': 'No listings found'})
            if active_status.is_active == status:
                raise ValidationError(
                    {'Status': f'The status is already set to {status}'}
                )
            result = model.objects(**{filter_by: listing_id}).update_one(
                set__is_active=status
            )
            if result == 0:
                raise DoesNotExist(
                    f'{model.__name__}: listing_id {listing_id} does not exist'
                )
            return True
        except OperationError as oe:
            raise OperationError(f'flip_status: Operation error: {oe}')

    @staticmethod
    def listsync(data, _id):
        '''
        Save listing doc to listsync collection.
        '''
        from helpers import ListSync

        required_fields = [
            'user_id',
            'category',
            'title',
            'location',
            'created_at',
        ]
        missing_fields = [
            field for field in required_fields if field not in data
        ]

        if missing_fields:
            raise ValidationError(
                f'Missing required fields: {", ".join(missing_fields)}'
            )
        obj = {
            'user_id': data['user_id'],
            'listing_id': str(_id),
            'category': data['category'],
            'subcategory': data['subcategory'],
            'title': data['title'],
            'location': data['location'],
            'created_at': data['created_at'],
        }
        price = (
            data.get('service_fee')
            or data.get('ticket_price')
            or data.get('price')
        )
        # Price range
        if data.get('salary_range'):
            obj['salary_range'] = data['salary_range']

        obj['price'] = price

        # Pictures
        if data.get('pictures'):
            obj['pictures'] = data['pictures']

        list_sync_entry = ListSync(**obj)
        list_sync_entry.save()
