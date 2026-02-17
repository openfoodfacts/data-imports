"""Field mapping from EPREL API names to Open Products Facts naming conventions.

Maps the raw EPREL API response fields for smartphones/tablets to the
colon-separated hierarchical field names used by Open Products Facts (OPF).
"""

# Auto-generated OPF field names (not directly from EPREL API fields)
OPF_FIELD_EC_ENERGY_LABEL_URL = "ec_energy_label:url"
OPF_FIELD_EC_ENERGY_LABEL_SVG_URL = "ec_energy_label:svg_url"
OPF_FIELD_IP_RATING_NUMBER = "ingress_protection_rating:ip:number"

# Mapping of EPREL API field names to OPF field names for smartphones.
# Only fields that have a direct EPREL source are included.
# Fields like color, camera specs, RAM, dimensions, etc. are NOT available
# from EPREL and must come from other data sources.
SMARTPHONES_FIELD_MAP = {
    # Product identification
    "supplierOrTrademark": "brands",
    "modelIdentifier": "manufacturer:reference_number",
    "eprelRegistrationNumber": "eprel_id",
    "deviceType": "device_type",
    # Barcodes (when available from EPREL)
    "gtin": "code",
    "ean": "code",
    "barcode": "code",
    # Supplier / producer contact information
    "supplierName": "supplier:name",
    "supplierAddress": "supplier:address",
    "supplierContact": "supplier:contact",
    "supplierEmail": "supplier:email",
    "supplierPhone": "supplier:phone",
    "supplierWebsite": "supplier:website",
    "contactAddress": "supplier:contact_address",
    "tradeMark": "supplier:trademark",
    "dealerName": "dealer:name",
    "dealerAddress": "dealer:address",
    # Energy & repairability
    "energyClass": "energy_efficiency_class:eu",
    "repairabilityClass": "repairability_class:eu",
    "repairabilityIndex": "repairability_index:eu",
    "onMarketStartDate": "release_date",
    "guaranteeDuration": "guarantee_duration:months",
    "minYearsSoftwareUpdates": "consumer_electronics:min_years_software_updates",
    # Battery
    "ratedBatteryCapacity": "consumer_electronics:battery_capacity:mah",
    "batteryEndurancePerCycle": "battery_autonomy_per_cycle:eu:hours_min",
    "batteryEnduranceInCycles": "battery_endurance_in_cycles:eu",
    "batteryCyclesFromPDF": "battery_lifespan_in_cycles:eu:higher_or_equal_to",
    "batteryUserReplaceable": "consumer_electronics:battery_user_replaceable",
    # Charger
    "chargerRequiredOutputPower": "consumer_electronics:charger_output_power:w",
    "chargerReceptacleType": "consumer_electronics:charger_receptacle_type",
    # Device characteristics
    "operatingSystem": "consumer_electronics:initial_operating_system",
    "isFoldable": "consumer_electronics:is_foldable",
    # Protection ratings
    "ingressProtectionRating": "ingress_protection_rating:ip",
    "ingressProtectionRatingSolid": "ingress_protection_rating:ip:solid",
    "ingressProtectionRatingWater": "ingress_protection_rating:ip:water",
    "immersionDepthWater": "ingress_protection_rating:ip:immersion_depth:m",
    "screenScratchResistance": "consumer_electronics:screen_scratch_resistance:mohs",
    "repeatedFreeFallReliabilityClass": "repeated_free_fall_reliability_class:eu",
    "fallsWithoutDefect": "consumer_electronics:falls_without_defect",
    # Repairability scores
    "disassemblyDepthScore": "repairability_score:eu:disassembly_depth",
    "fastenersScore": "repairability_score:eu:fasteners",
    "toolsScore": "repairability_score:eu:tools",
    "sparePartScore": "repairability_score:eu:spare_parts",
    "repairInfoScore": "repairability_score:eu:repair_info",
    # Repair links
    "webLinkRepairInstructions": "consumer_electronics:repair_instructions:url",
    "webLinkInfoSparePartsAvailability": "consumer_electronics:spare_parts_info:url",
}

# EPREL fields that are known NOT to be available from the API.
# These must come from other data sources (e.g. manual entry, other databases).
# Listed here for documentation purposes.
OPF_FIELDS_NOT_IN_EPREL = [
    "color",
    "consumer_electronics:front_camera_resolution:mpx",
    "consumer_electronics:initial_operating_system:version",
    "consumer_electronics:most_recent_network_generation",
    "consumer_electronics:number_of_sim_slots:esim",
    "consumer_electronics:number_of_sim_slots:physical",
    "consumer_electronics:ram_memory:capacity:gb",
    "consumer_electronics:rear_camera_resolution:mpx",
    "consumer_electronics:rom_memory:capacity:gb",
    "consumer_electronics:screen_size:diagonal:inch",
    "consumer_electronics:sd_card_max_capacity:gb",
    "consumer_electronics:sim_card_slot_type",
    "consumer_electronics:nb_of_rear_cameras",
    "depth:mm",
    "height:mm",
    "weight:g",
    "width:mm",
    "manufacturer:serie_reference",
    "manufacturer:suggested_retail_price:eu:eur",
]


def map_product_fields(product, field_map=None, category="smartphones"):
    """Rename a product dict's keys from EPREL API names to OPF names.

    Args:
        product: Dictionary with EPREL API field names as keys.
        field_map: Mapping dict (EPREL name -> OPF name).
                   Defaults to SMARTPHONES_FIELD_MAP.
        category: Product category for generating label URLs.

    Returns:
        New dictionary with OPF field names. Fields not in the mapping
        are preserved with an "eprel:" prefix. The ec_energy_label:url
        and ec_energy_label:svg_url are auto-generated from the EPREL
        registration number.
    """
    if field_map is None:
        field_map = SMARTPHONES_FIELD_MAP

    # Lazy import to avoid circular dependency
    from eprel_client import PRODUCT_CATEGORIES, EPREL_LABELS_BASE_URL

    mapped = {}
    eprel_id = product.get("eprelRegistrationNumber")

    for key, value in product.items():
        opf_key = field_map.get(key)
        if opf_key:
            # For "code", only set if value is non-empty (barcode)
            if opf_key == "code":
                val = str(value).strip() if value else ""
                if val and val.lower() not in ("none", "null"):
                    mapped[opf_key] = val
            else:
                mapped[opf_key] = value
        else:
            mapped[f"eprel:{key}"] = value

    category_path = PRODUCT_CATEGORIES.get(category, category)

    # Auto-generate the EPREL energy label URL
    if eprel_id is not None:
        mapped[OPF_FIELD_EC_ENERGY_LABEL_URL] = (
            f"https://eprel.ec.europa.eu/screen/product/"
            f"{category_path}/{eprel_id}"
            f"?navigatingfrom=qr"
        )
        # Auto-generate the label SVG URL
        mapped[OPF_FIELD_EC_ENERGY_LABEL_SVG_URL] = (
            f"{EPREL_LABELS_BASE_URL}/{category_path}/"
            f"Label_{eprel_id}.svg"
        )

    # Extract numeric IP rating from the string (e.g., "IP68" -> 68)
    ip_rating = product.get("ingressProtectionRating", "")
    if ip_rating and ip_rating.startswith("IP"):
        try:
            ip_number = int(ip_rating[2:])
            mapped[OPF_FIELD_IP_RATING_NUMBER] = ip_number
        except ValueError:
            pass

    return mapped


def get_opf_csv_headers(field_map=None):
    """Return the list of OPF field names for CSV headers.

    Args:
        field_map: Mapping dict. Defaults to SMARTPHONES_FIELD_MAP.

    Returns:
        Sorted list of OPF field names plus auto-generated fields.
    """
    if field_map is None:
        field_map = SMARTPHONES_FIELD_MAP
    headers = sorted(set(field_map.values()))
    headers.append(OPF_FIELD_EC_ENERGY_LABEL_URL)
    headers.append(OPF_FIELD_EC_ENERGY_LABEL_SVG_URL)
    headers.append(OPF_FIELD_IP_RATING_NUMBER)
    return headers
