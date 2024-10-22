'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
Listsync helper class.
---------------------------------------------------
'''

from mongoengine import DoesNotExist, OperationError

from listings.models import ListSync


class ListSynchronize:
    '''
    List synchronization helper class.
    '''

    @staticmethod
    def flip_status(listing_id, status, model=ListSync):
        '''
        flip status for certain list.
        '''
        try:
            if model == ListSync:
                result = model.objects(listing_id=listing_id).update_one(
                    set__is_active=status
                )
            else:
                result = model.objects(id=listing_id).update_one(
                    set__is_active=status
                )
            if result == 0:
                raise DoesNotExist(
                    f'ListSync: listing_id {listing_id} does not exist'
                )
            return True
        except OperationError as oe:
            raise OperationError(f"flip status: Operation error: {oe}")

    @staticmethod
    def listsync(data, _id):
        '''
        Save listing doc to listsync collection.
        '''
        obj = {
            'user_id': data['user_id'],
            'listing_id': str(_id),
            'category': data['category'],
            'title': data['title'],
            'location': data['location'],
            'created_at': data['created_at'],
        }

        # Price range
        if data.get('salary_range'):
            obj['salary_range'] = data['salary_range']
        elif data.get('service_fee'):
            obj['price'] = data['service_fee']
        elif data.get('ticket_price'):
            obj['price'] = data['ticket_price']
        else:
            obj['price'] = data['price']

        # Pictures
        if data.get('pictures'):
            obj['pictures'] = data['pictures']

        list_sync_entry = ListSync(**obj)
        list_sync_entry.save()
