'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
Search of Listings endpoints.
---------------------------------------------------
'''

from mongoengine import Q
from django.db.models import Q as SQL_Q
from rest_framework import generics, status
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated,
)

from helpers import ListSync
from users.models.users import User
from helpers import handle_exceptions, response
from listings.api.paginate_listing import Pagination
from listings.serializers import ListsyncSerializer
from rest_framework.exceptions import ValidationError


class Search(generics.ListAPIView):

    pagination_class = Pagination
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ListsyncSerializer

    @handle_exceptions
    def get_queryset(self):
        user_id = self.request.user.id
        search = self.request.data.get('search').strip()
        if len(search) < 5:
            raise ValidationError({'Search': 'More than 5 characters Required'})

        if not search:
            raise ValidationError({'Search': 'Search cannot be empty'})
        try:
            queryset = ListSync.objects.filter(
                Q(title__regex=r'(?i)' + search)
                | Q(category__regex=r'(?i)' + search)
                | Q(subcategory__regex=r'(?i)' + search)
                | Q(keywords__regex=r'(?i)' + search)
            )
        except Exception as exc:
            raise ValidationError({'Listsync': str(exc)})
        if user_id:
            user = User.objects.filter(id=user_id).first()
            if not user.recent_searches or user.recent_searches[-1] != search:
                if len(user.recent_searches) == 10:
                    user.recent_searches.pop(0)
                user.recent_searches.append(search)
                user.save()
        return queryset


class RecentSearches(generics.CreateAPIView):

    permission_classes = [IsAuthenticated]

    @handle_exceptions
    def get(self, request):
        user_id = request.user.id
        user = User.objects.filter(id=user_id).first()
        user_searches = user.recent_searches
        recent_searches = {
            i + 1: item for i, item in enumerate(user_searches)
        }  # convert to dict
        return response(
            status=status.HTTP_200_OK,
            message='Recent Searches Found',
            data=recent_searches,
        )


class DeleteSearches(generics.DestroyAPIView):

    permission_classes = [IsAuthenticated]

    @handle_exceptions
    def delete(self, request, *args, **kwargs):
        user_id = request.user.id
        user = User.objects.filter(id=user_id).first()
        user.recent_searches.clear()
        user.save()
        return response(
            status=status.HTTP_204_NO_CONTENT,
            message='Recent Searches Deleted',
            data=[],
        )
