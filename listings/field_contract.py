'''
Canonical listing field/value aliases.

Clients historically send display labels, camelCase, and typos.
Normalize them to the MongoEngine field names and choice values
before serializer validation.
'''

from helpers.normalize import _normalize_token

# Incoming key → canonical model field
FIELD_ALIASES = {
    'loadcapcity': 'Load_capacity',
    'loadcapacity': 'Load_capacity',
    'load_capacity': 'Load_capacity',
    'partname': 'part_name',
    'partName': 'part_name',
    'fueltype': 'fuel_type',
    'fuelType': 'fuel_type',
    'transmission': 'transmission',
    'Transmission': 'transmission',
    'purpose': 'purpose',
    'Purpose': 'purpose',
    'numberofdoors': 'number_of_doors',
    'Number of Doors': 'number_of_doors',
    'number_of_doors': 'number_of_doors',
    'forsale': 'for_sale',
    'For Sale': 'for_sale',
    'rentals': 'rentals',
    'Rentals': 'rentals',
    'vehicletype': 'vehicle_type',
    'duration': 'rental_duration',
    'biketype': 'bike_type',
    'listing_address': 'location',
    'address': 'location',
    'parking_availability_and_cost': 'parking_and_cost',
    'service_available': 'service_delivery_method',
}

_CONTEXT_FIELD_ALIASES = {
    'bike': {'type': 'bike_type'},
    'outdooractivities': {'processor': 'activity_type'},
    'activities': {
        'activity': 'activity_type',
        'required': 'equipment_required',
        'processor': 'activity_type',
    },
}

# Context-sensitive keys (depend on subcategory)
_LENGTH_BY_SUBCATEGORY = {
    'boat': 'boat_length',
    'van': 'passenger_capacity',
}

# Display / mixed-case values → canonical choice values
VALUE_ALIASES = {
    'automatic': 'AUTOMATIC',
    'manual': 'MANUAL',
    'sale': 'SALE',
    'rental': 'RENTAL',
    'yes': 'YES',
    'no': 'NO',
    'new': 'NEW',
    'used': 'USED',
    '4': '4/5',
    '3': '1/3',
    '5': '4/5',
    'remotely': 'REMOTELY',
    'remote': 'REMOTE',
    'cattering': 'CATERING',
    'carpentary': 'CARPENTRY',
    'long-distance': 'LONG-DISTANCE',
    'local-distance': 'LONG-DISTANCE',
    'clonial coffee': 'COLONIAL COFFEE',
}

CHOICE_FIELDS = {
    'transmission',
    'condition',
    'purpose',
    'negotiable',
    'for_sale',
    'rentals',
    'number_of_doors',
    'furnished',
    'basement',
    'lease_terms',
    'credit_score',
    'utilities_included',
    'access_to_amenities',
    'additional_fees',
    'pet_policy',
    'renters_insurance_requirement',
    'security_measures',
    'lease_managed_by',
    'bathroom_type',
    'kitchen_access_type',
    'laundry_facilities',
    'bedroom_additional_Fees',
    'smoking_policy',
    'security_features',
    'preferred_occupants',
    'certifications',
    'insurance',
    'payment_options',
    'cleaning_services',
    'eco_friendly_product',
    'provided_equipment',
    'handyman_services',
    'same_day_service',
    'driving_services',
    'vehicle_type',
    'landscaping_services',
    'regular_maintenance',
    'seasonal_service',
    'initial_consultation',
    'consultancy_services',
    'offered_services',
    'automation_services',
    'classes_format',
    'training_services',
    'session_format',
    'personalised_fitness_plan',
    'group_session',
    'construction_services',
    'expertise_level',
    'technology_services',
    'service_delivery_method',
    'ongoing_support_maintenance',
    'visa_services',
    'free_appointment',
    'event_type',
    'events_services',
    'customizable_package',
    'movers_services',
    'packing_material',
    'insurance_for_goods',
    'farm_services',
    'delivery_availability',
    'organic_sourced',
    'regular_delivery_option',
    'photography_services',
    'different_packages',
    'recurring_services',
    'interior_services',
    'material_furniture_Selection',
    'rendering_visualizations',
    'service_availability',
    'homemade_service',
    'insurance_service',
    'homecare_service',
    'menu_customization',
}

# Optional numeric fields Flutter used to send as "null/NOT specified".
OPTIONAL_INT_FIELDS = {
    'mileage',
    'Load_capacity',
    'boat_length',
    'passenger_capacity',
    'bedrooms',
    'bathrooms',
    'hoa_fees',
    'number_of_floors',
    'security_deposit',
    'pricing_structure',
    'class_duration',
    'audience_size',
}


def is_placeholder_value(value):
    '''True for empty / "null/Not specified" style client sentinels.'''
    if value is None:
        return True
    if not isinstance(value, str):
        return False
    compact = ' '.join(value.strip().lower().split())
    squeezed = compact.replace(' ', '').replace('/', '')
    return compact in {
        '',
        'null',
        'none',
        'not specified',
        'null/not specified',
        'null/notspecified',
        'no, chip selected',
    } or squeezed in {'nullnotspecified', 'notspecified'}


def coerce_optional_int_fields(payload):
    '''Parse optional ints; drop placeholders / unparseable strings.'''
    if not isinstance(payload, dict):
        return payload
    for field in OPTIONAL_INT_FIELDS:
        if field not in payload:
            continue
        value = payload[field]
        if is_placeholder_value(value):
            payload.pop(field)
            continue
        if isinstance(value, bool):
            payload.pop(field)
            continue
        if isinstance(value, int):
            continue
        try:
            text = str(value).strip().replace(',', '')
            payload[field] = int(float(text))
        except (TypeError, ValueError):
            payload.pop(field)
    year = payload.get('year')
    if year is not None and not isinstance(year, bool):
        try:
            payload['year'] = int(float(str(year).strip().replace(',', '')))
        except (TypeError, ValueError):
            pass
    return payload


def apply_field_aliases(payload, subcategory=None):
    '''Return a copy of ``payload`` with aliased keys/values normalized.'''
    if not isinstance(payload, dict):
        return payload

    sub_key = _normalize_token(subcategory or payload.get('subcategory'))
    context_aliases = _CONTEXT_FIELD_ALIASES.get(sub_key, {})
    remapped = {}
    for key, value in payload.items():
        canonical = context_aliases.get(key) or FIELD_ALIASES.get(key)
        if canonical is None and isinstance(key, str):
            normalized_key = _normalize_token(key)
            for alias, target in {**FIELD_ALIASES, **context_aliases}.items():
                if _normalize_token(alias) == normalized_key:
                    canonical = target
                    break
        if key == 'length' or (
            isinstance(key, str) and _normalize_token(key) == 'length'
        ):
            canonical = _LENGTH_BY_SUBCATEGORY.get(sub_key, key)
        remapped[canonical or key] = value

    for field in CHOICE_FIELDS:
        if field not in remapped:
            continue
        raw = remapped[field]
        if is_placeholder_value(raw):
            remapped.pop(field)
            continue
        if not isinstance(raw, str):
            continue
        alias = VALUE_ALIASES.get(raw.strip().lower())
        if alias:
            remapped[field] = alias
        elif raw.strip().upper() in ('YES', 'NO', 'NEW', 'USED', 'SALE', 'RENTAL', 'AUTOMATIC', 'MANUAL'):
            remapped[field] = raw.strip().upper()

    location = remapped.get('location') or remapped.get('listing_address')
    if location not in (None, ''):
        remapped['location'] = str(location).strip()
    return remapped


def extract_coordinates(raw):
    '''Normalize GeoJSON / list / JSON-string coordinates to [lon, lat].'''
    if raw in (None, '', []):
        return None
    coords = raw
    if isinstance(raw, str):
        import json

        try:
            coords = json.loads(raw)
        except json.JSONDecodeError:
            return None
    if (
        isinstance(coords, dict)
        and coords.get('type') == 'Point'
        and isinstance(coords.get('coordinates'), (list, tuple))
        and len(coords['coordinates']) >= 2
    ):
        coords = coords['coordinates']
    if not isinstance(coords, (list, tuple)) or len(coords) != 2:
        return None
    try:
        lon, lat = float(coords[0]), float(coords[1])
    except (TypeError, ValueError):
        return None
    return [lon, lat]


def point_to_lon_lat(point):
    '''Extract [lon, lat] from a MongoEngine PointField value.'''
    if point is None:
        return None
    if isinstance(point, (list, tuple)) and len(point) == 2:
        return [float(point[0]), float(point[1])]
    if isinstance(point, dict):
        coords = point.get('coordinates')
        if isinstance(coords, (list, tuple)) and len(coords) >= 2:
            return [float(coords[0]), float(coords[1])]
    return None
