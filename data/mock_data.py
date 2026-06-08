MOCK_SUBSCRIBER_RECORDS = [
    {
        "tn": "3035550192",
        "street_address": "100 Colfax Ave.",
        "city": "Denver",
        "state": "CO",
        "zip_code": "80202",
        "unit": "",
        "notes": "High-density multi-tenant structure"
    },
    {
        "tn": "7205559843",
        "street_address": "2985 S Hudson St",
        "city": "Denver",
        "state": "CO",
        "zip_code": "80222",
        "unit": "",
        "notes": "Single-family dwelling"
    },
    {
        "tn": "3035554411",
        "street_address": "450 Broadway St.",
        "city": "Denver",
        "state": "CO",
        "zip_code": "80203",
        "unit": "Suite 200",
        "notes": "Cross-border municipal boundary hazard"
    }
]

MOCK_MUNICIPAL_GIS = {
    "100 COLFAX AVE": {
        "parcel_number": "01422-04-990",
        "legal_county": "DENVER",
        "requires_unit_number": True,
        "lat": 39.7397, "lon": -104.9848,
        "psap_id": "DEN_PSAP_04"
    },
    "2985 S HUDSON ST": {
        "parcel_number": "05243-00-112",
        "legal_county": "DENVER",
        "requires_unit_number": False,
        "lat": 39.6625, "lon": -104.9038,
        "psap_id": "DEN_PSAP_01"
    },
    "450 BROADWAY ST": {
        "parcel_number": "09811-12-340",
        "legal_county": "ARAPHOE",
        "requires_unit_number": True,
        "lat": 39.7256, "lon": -104.9875,
        "psap_id": "ARA_PSAP_02"
    }
}
