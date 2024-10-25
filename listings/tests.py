from django.test import TestCase

# Create your tests here.


# # Insert data into MongoDB
# for category_name, subcategory_list in CATEGORIES.items():
#     subcategories = [
#         Subcategory(id=bson.ObjectId(), name=sub) for sub in subcategory_list
#     ]
#     category = Category(
#         name=category_name,
#         description=f"{category_name} category",
#         subcategories=subcategories,
#     )
#     try:
#         category.save()
#     except Exception as e:
#         print(f"Error inserting {category_name}: {e}")
