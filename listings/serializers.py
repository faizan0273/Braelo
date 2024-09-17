'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
Serializer file for Listings based endpoints
---------------------------------------------------
'''

from .models.category import Category
from .models.category import Subcategory

from rest_framework_mongoengine import serializers


class SubcategorySerializer(serializers.EmbeddedDocumentSerializer):
    class Meta:
        model = Subcategory
        fields = ['name', 'description']


class CategorySerializer(serializers.DocumentSerializer):
    subcategories = SubcategorySerializer(many=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'subcategories']

    def validate_subcategories(self, subcategories):
        # Check for uniqueness of subcategory names within the category
        names = [subcat['name'] for subcat in subcategories]
        if len(names) != len(set(names)):
            raise serializers.ValidationError(
                "Subcategory names must be unique within a category."
            )
        return subcategories

    def create(self, validated_data):
        subcategories_data = validated_data.pop('subcategories', [])
        category = Category(**validated_data)

        # Add the subcategories
        for subcat_data in subcategories_data:
            subcategory = Subcategory(**subcat_data)
            category.subcategories.append(subcategory)

        category.save()
        return category

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get(
            'description', instance.description
        )

        # Handle updating subcategories
        subcategories_data = validated_data.get('subcategories')
        if subcategories_data:
            instance.subcategories = []
            for subcat_data in subcategories_data:
                subcategory = Subcategory(**subcat_data)
                instance.subcategories.append(subcategory)

        instance.save()
        return instance
