"""
forms_schema.py
Definizione dei campi di ciascuna delle 15 maschere, cosi' come sono nel
programma attuale (nomi campo, etichette, tipo). Il rendering vero e proprio
e' fatto da ui_dynamic_form.py in base a questi dati.

Tipi di campo:
  text          - casella di testo singola riga
  textarea      - casella di testo multiriga (Comments, Nota_Privata...)
  dropdown      - menu a tendina, valori gestiti in Amministrazione > Parametri
  dropdown_free - menu a tendina + casella di testo libera accanto
                  (es. "Standard of Inspection": scegli la norma dal menu,
                  poi eventuali dettagli extra nel testo libero)
  date          - data
"""

# Blocco campi ripetuto in quasi tutte le maschere sul lato destro
def _right_common(extra_top=None, extra_bottom=None, competent_person=False, well_rig=False,
                   schedule=False):
    fields = list(extra_top or [])
    fields += [
        {"key": "customer", "label": "Customer", "type": "dropdown"},
        {"key": "place_of_inspection", "label": "Place of Inspection", "type": "text"},
        {"key": "gruppo", "label": "Gruppo", "type": "text"},
    ]
    if well_rig:
        fields.append({"key": "well_rig", "label": "Well/Rig", "type": "text"})
    if schedule:
        fields += [
            {"key": "shedule_months", "label": "Shedule Months", "type": "dropdown"},
            {"key": "expire_data", "label": "Expire Data", "type": "date"},
        ]
    fields += [
        {"key": "data_report", "label": "Data Report", "type": "date"},
        {"key": "data_creation", "label": "Data Creation", "type": "date"},
        {"key": "wo", "label": "WO", "type": "dropdown"},
        {"key": "po", "label": "PO", "type": "dropdown"},
        {"key": "inspector", "label": "Inspector", "type": "dropdown"},
    ]
    if competent_person:
        fields.append({"key": "competent_person", "label": "Competent Person", "type": "dropdown"})
    fields += list(extra_bottom or [])
    return fields


def _mag_particle_block():
    """Blocco tecnica di magnetizzazione, usato in DrillPipe, DrillCollar, HWDP, Rotary."""
    return [
        {"key": "magnetizing_technique", "label": "Magnetizing Technique", "type": "dropdown_free"},
        {"key": "current_type", "label": "Current Type", "type": "dropdown_free"},
        {"key": "field_direction", "label": "Field Direction", "type": "dropdown_free"},
        {"key": "field_strenght", "label": "Field Strenght", "type": "dropdown_free"},
    ]


NDT_STD_FIELDS = [
    {"key": "tool_description", "label": "Tool Description", "type": "text"},
    {"key": "serial_number", "label": "Serial Number", "type": "text"},
    {"key": "outcome_inspection", "label": "Outcome Inspection", "type": "dropdown"},
    {"key": "extension", "label": "Extension", "type": "text"},
    {"key": "comments", "label": "Comments", "type": "textarea"},
    {"key": "standard_of_inspection", "label": "Standard of Inspection", "type": "dropdown_free"},
]

EQUIPMENT_TABLE_COLUMNS = ["Eq.", "SN", "Calibration Data", "Due Data"]


FORM_SCHEMAS = {

    "Dry Penetrant": {
        "title": "DYE PENETRANT",
        "left_fields": NDT_STD_FIELDS + [
            {"key": "dwell_time", "label": "Dwell_Time (10-60 min; 20 min a 10°C)", "type": "text"},
            {"key": "developing_time", "label": "Developing_Time (10-30 min)", "type": "text"},
            {"key": "temperature", "label": "Temperature (4°C - 51°C)", "type": "text"},
            {"key": "light_intensity", "label": "Light_Intensity (> 1100 lux)", "type": "text"},
            {"key": "material", "label": "Material", "type": "dropdown"},
            {"key": "surface_condition", "label": "Surface Condition", "type": "dropdown"},
            {"key": "method_used", "label": "Method Used", "type": "dropdown"},
            {"key": "penetrant_type", "label": "Penetrant Type", "type": "dropdown"},
            {"key": "developer_type", "label": "Developer Type", "type": "dropdown"},
            {"key": "removal_type", "label": "Removal Type", "type": "dropdown"},
            {"key": "nota_privata", "label": "Nota Privata", "type": "textarea"},
        ],
        "right_fields": _right_common(),
        "photo_slots": 4,
        "equipment_table": True,
    },

    "MPI": {
        "title": "MPI",
        "left_fields": NDT_STD_FIELDS + [
            {"key": "material", "label": "Material", "type": "dropdown"},
            {"key": "surface_condition", "label": "Surface Condition", "type": "dropdown"},
            {"key": "magnetizing_technique", "label": "Magnetizing Technique", "type": "dropdown_free"},
            {"key": "current_type", "label": "Current Type", "type": "dropdown"},
            {"key": "field_direction", "label": "Field Dir.", "type": "dropdown"},
            {"key": "field_strenght", "label": "Field Strenght", "type": "dropdown"},
            {"key": "type_of_joint", "label": "Type of Joint", "type": "text"},
            {"key": "welding_process", "label": "Welding Process", "type": "text"},
            {"key": "heat_treatment", "label": "Heat Treatment", "type": "text"},
            {"key": "nota_privata", "label": "Nota Privata", "type": "textarea"},
        ],
        "right_fields": _right_common(),
        "photo_slots": 4,
        "equipment_table": True,
    },

    "Eddy Current": {
        "title": "EDDY CURRENT",
        "left_fields": NDT_STD_FIELDS + [
            {"key": "material", "label": "Material", "type": "dropdown"},
            {"key": "surface_condition", "label": "Surface Condition", "type": "dropdown"},
            {"key": "coating_depth", "label": "Coating Depth", "type": "text"},
            {"key": "type_of_joint", "label": "Type of Joint", "type": "text"},
            {"key": "welding_process", "label": "Welding Process", "type": "text"},
            {"key": "heat_treatment", "label": "Heat Treatment", "type": "text"},
            {"key": "freq_khz", "label": "Freq. (Khz)", "type": "text"},
            {"key": "db", "label": "dB", "type": "text"},
            {"key": "nota_privata", "label": "Nota Privata", "type": "textarea"},
        ],
        "right_fields": _right_common(),
        "photo_slots": 4,
        "equipment_table": True,
    },

    "Visual": {
        "title": "VISUAL",
        "left_fields": NDT_STD_FIELDS + [
            {"key": "material", "label": "Material", "type": "dropdown"},
            {"key": "surface_condition", "label": "Surface Condition", "type": "dropdown"},
            {"key": "light_type", "label": "Light Type", "type": "dropdown"},
            {"key": "type_of_joint", "label": "Type of Joint", "type": "text"},
            {"key": "welding_process", "label": "Welding Process", "type": "text"},
            {"key": "nota_privata", "label": "Nota Privata", "type": "textarea"},
        ],
        "right_fields": _right_common(),
        "photo_slots": 4,
        "equipment_table": True,
    },

    "Ultrasonic": {
        "title": "ULTRASONIC",
        "left_fields": NDT_STD_FIELDS + [
            {"key": "material", "label": "Material", "type": "dropdown"},
            {"key": "surface_condition", "label": "Surface Condition", "type": "dropdown"},
            {"key": "reference_block", "label": "Reference Block", "type": "text"},
            {"key": "drawing", "label": "Drawing", "type": "text"},
            {"key": "working_step", "label": "Working Step", "type": "text"},
            {"key": "coupling_used", "label": "Coupling Used", "type": "text"},
            {"key": "scanning_position_1", "label": "Scanning Position 1", "type": "dropdown"},
            {"key": "scanning_position_2", "label": "Scanning Position 2", "type": "dropdown"},
            {"key": "scanning_position_3", "label": "Scanning Position 3", "type": "dropdown"},
            {"key": "scanning_position_4", "label": "Scanning Position 4", "type": "dropdown"},
            {"key": "scanning_position_5", "label": "Scanning Position 5", "type": "dropdown"},
            {"key": "ut_probe_1", "label": "UT-Probe 1", "type": "text"},
            {"key": "db_position_1", "label": "dB Position 1", "type": "text"},
            {"key": "ut_probe_2", "label": "UT-Probe 2", "type": "text"},
            {"key": "db_position_2", "label": "dB Position 2", "type": "text"},
            {"key": "ut_probe_3", "label": "UT-Probe 3", "type": "text"},
            {"key": "db_position_3", "label": "dB Position 3", "type": "text"},
            {"key": "nota_privata", "label": "Nota Privata", "type": "textarea"},
        ],
        "right_fields": _right_common(),
        "photo_slots": 4,
        "equipment_table": True,
    },

    "UT-Thickness": {
        "title": "UT-THICKNESS",
        "left_fields": NDT_STD_FIELDS + [
            {"key": "material", "label": "Material", "type": "dropdown"},
            {"key": "surface_condition", "label": "Surface Condition", "type": "dropdown"},
            {"key": "reference_block", "label": "Reference Block", "type": "text"},
            {"key": "drawing", "label": "Drawing", "type": "text"},
            {"key": "working_step", "label": "Working Step", "type": "text"},
            {"key": "coupling_used", "label": "Coupling Used", "type": "text"},
            {"key": "nota_privata", "label": "Nota Privata", "type": "textarea"},
        ],
        "right_fields": _right_common(),
        "photo_slots": 0,
        "equipment_table": True,
        "detail_table": {
            "label": "Letture spessore",
            "columns": ["Position", "Reading1", "Reading2", "Reading3", "Reading4", "Reading5",
                        "Reading6", "Reading7", "Reading8", "Reading9", "Reading10"],
        },
    },

    "Lifting Gear": {
        "title": "LIFTING GEAR",
        "left_fields": [
            {"key": "tool_description", "label": "Tool Description", "type": "text"},
            {"key": "serial_number", "label": "Serial Number", "type": "text"},
            {"key": "safe_to_operate", "label": "Is this equipment safe to operate?", "type": "dropdown"},
            {"key": "outcome_inspection", "label": "Outcome of Inspection", "type": "dropdown"},
            {"key": "extension", "label": "Extension", "type": "text"},
            {"key": "comments", "label": "Comments", "type": "textarea"},
            {"key": "standard_of_inspection", "label": "Standard of Inspection", "type": "dropdown_free"},
            {"key": "swl_ton", "label": "SWL (ton)", "type": "text"},
            {"key": "size_mm", "label": "Size (mm)", "type": "text"},
            {"key": "lenght_mt", "label": "Lenght (mt)", "type": "text"},
            {"key": "grade", "label": "Grade", "type": "text"},
            {"key": "material", "label": "Material", "type": "dropdown"},
            {"key": "ndt_type_liftingset", "label": "NDT Type LiftingSet", "type": "dropdown"},
            {"key": "associated_of", "label": "Associated of", "type": "text"},
            {"key": "color_code", "label": "Color Code", "type": "text"},
            {"key": "department", "label": "Department", "type": "text"},
            {"key": "tests_carried_out", "label": "Particolari delle prove eseguite", "type": "textarea"},
            {"key": "first_examination", "label": "Prima esaminazione dopo installazione/montaggio?", "type": "dropdown"},
            {"key": "installed_correctly", "label": "Se si', installato correttamente?", "type": "dropdown"},
            {"key": "examination_scheme", "label": "Esame secondo schema di esaminazione?", "type": "dropdown"},
            {"key": "exceptional_circumstances", "label": "Esame dopo circostanze eccezionali?", "type": "dropdown"},
            {"key": "defect_found", "label": "Difetto rilevato - pericolo imminente?", "type": "dropdown"},
            {"key": "nota_privata", "label": "Nota Privata", "type": "textarea"},
        ],
        "right_fields": _right_common(competent_person=True, schedule=True),
        "photo_slots": 4,
        "equipment_table": False,
    },

    "Lifting Gear 2": {
        "title": "LIFTING GEAR 2",
        "left_fields": [],
        "right_fields": [
            {"key": "customer", "label": "Customer", "type": "dropdown"},
            {"key": "place_of_inspection", "label": "Place of Inspection", "type": "text"},
            {"key": "wo", "label": "WO", "type": "dropdown"},
            {"key": "po", "label": "PO", "type": "dropdown"},
            {"key": "data_creation", "label": "Data Creation", "type": "date"},
            {"key": "inspector", "label": "Inspector", "type": "dropdown"},
            {"key": "competent_person", "label": "Competent Person", "type": "dropdown"},
            {"key": "nota_privata", "label": "Nota Privata", "type": "textarea"},
        ],
        "photo_slots": 0,
        "equipment_table": False,
        "detail_table": {
            "label": "Elenco elementi (righe multiple per certificato)",
            "columns": ["Serial_Number", "Tool_Description", "SWL_ton", "Size_mm", "Lenght_mt", "Grade",
                        "Standard_Inspection", "Data_Report", "Shedule_Months",
                        "SAFE_TO_OPERATE", "OUTCOME_INSPECTION", "Associated_of", "Color_Code", "Department"],
        },
    },

    "Proof Load Test": {
        "title": "LOAD TEST",
        "left_fields": [
            {"key": "tool_description", "label": "Tool Description", "type": "text"},
            {"key": "serial_number", "label": "Serial Number", "type": "text"},
            {"key": "outcome_inspection", "label": "Outcome Inspection", "type": "dropdown"},
            {"key": "comments", "label": "Comments", "type": "textarea"},
            {"key": "standard_of_inspection", "label": "Standard of Inspection", "type": "dropdown_free"},
            {"key": "swl_or_work_press", "label": "SWL (ton) or Work Press. (psi)", "type": "text"},
            {"key": "size", "label": "Size", "type": "text"},
            {"key": "load_test", "label": "Load Test (Ton) or Test Press. (psi)", "type": "text"},
            {"key": "safety_factor", "label": "Safety Factor", "type": "text"},
            {"key": "cylinder_size_cm2", "label": "Cylinder Size (cm2)", "type": "text"},
            {"key": "pressure_of_test_bar", "label": "Pressure of Test (bar)", "type": "dropdown"},
            {"key": "material", "label": "Material", "type": "dropdown"},
            {"key": "associated_of", "label": "Associated of", "type": "text"},
            {"key": "department", "label": "Department", "type": "text"},
            {"key": "marking_requirements", "label": "Marking Mandatory Requirements", "type": "text"},
            {"key": "general_condition", "label": "General Condition", "type": "text"},
            {"key": "nota_privata", "label": "Nota Privata", "type": "textarea"},
        ],
        "right_fields": _right_common(competent_person=True, schedule=True),
        "photo_slots": 0,
        "equipment_table": False,
    },

    "Rotary Tool Description": {
        "title": "ROTARY",
        "left_fields": [
            {"key": "tool_description", "label": "Tool Description", "type": "text"},
            {"key": "serial_number", "label": "Serial Number", "type": "text"},
            {"key": "extension", "label": "Extension", "type": "text"},
            {"key": "comments", "label": "Comments", "type": "textarea"},
            {"key": "standard_of_inspection", "label": "Standard of Inspection", "type": "dropdown_free"},
            {"key": "material", "label": "Material", "type": "dropdown"},
            {"key": "surface_condition", "label": "Surface Condition", "type": "dropdown"},
        ] + _mag_particle_block() + [
            {"key": "nota_privata", "label": "Nota Privata", "type": "textarea"},
        ],
        "right_fields": _right_common(well_rig=True),
        "photo_slots": 0,
        "equipment_table": True,
        "detail_table": {
            "label": "Connessioni",
            "columns": ["Connection Side", "Type Connection", "OD", "ID", "Lenght Thread", "Bevel",
                        "BB-SRG Diam", "BB-SRG Lenght", "Counterbore Diam", "Counterbore Depth",
                        "Tong Space - Fishing Neck", "Condition", "Total Lenght",
                        "Body Visual Condition", "Body MPI Condition", "Outcome Inspection"],
        },
    },

    "Thorough Examination": {
        "title": "THOROUGHT EXAMINATION",
        "left_fields": [
            {"key": "category", "label": "Categoria (Offshore Basket, Skid, Container...)", "type": "dropdown"},
            {"key": "tool_description", "label": "Tool Description", "type": "text"},
            {"key": "serial_number", "label": "Serial Number", "type": "text"},
            {"key": "outcome_inspection", "label": "Outcome Inspection", "type": "dropdown"},
            {"key": "department", "label": "Department", "type": "text"},
            {"key": "comments", "label": "Comments", "type": "textarea"},
            {"key": "standard_of_inspection", "label": "Standard of Inspection", "type": "dropdown_free"},
            {"key": "tare_kg", "label": "Tare (Kg)", "type": "text"},
            {"key": "payload_kg", "label": "PayLoad (Kg)", "type": "text"},
            {"key": "gross_weight_kg", "label": "Gross Weight (Kg)", "type": "text"},
            {"key": "dimension_lxwxh_mt", "label": "Dimension L x W x H (mt)", "type": "text"},
            {"key": "manufacturing_year", "label": "Manufacturing Year", "type": "text"},
            {"key": "design_temperature", "label": "Design Temperature", "type": "text"},
            {"key": "ndt_type_basket", "label": "NDT Type Basket", "type": "dropdown"},
            {"key": "last_ndt_data", "label": "Last NDT Data", "type": "date"},
            {"key": "last_ndt_report", "label": "Last NDT N. Report", "type": "text"},
            {"key": "sling_type", "label": "Sling Type", "type": "text"},
            {"key": "sling_sn", "label": "Sling SN", "type": "text"},
            {"key": "sling_swl_ton", "label": "Sling SWL (ton)", "type": "text"},
            {"key": "sling_size_mm", "label": "Sling Size (mm)", "type": "text"},
            {"key": "sling_lenght_mt", "label": "Sling Lenght (mt)", "type": "text"},
            {"key": "sling_angle", "label": "Sling Angle (°)", "type": "text"},
            {"key": "standard_liftingset", "label": "Standard Inspect. LiftingSet", "type": "dropdown"},
            {"key": "ndt_type_liftingset", "label": "NDT Type LiftingSet", "type": "dropdown"},
            {"key": "shackle_sn", "label": "Shackle SN", "type": "text"},
            {"key": "shackle_swl_ton", "label": "Shackle SWL (ton)", "type": "text"},
            {"key": "shackle_size_inch", "label": "Shackle Size (inch)", "type": "text"},
            {"key": "color_code", "label": "Color Code", "type": "text"},
            {"key": "insp_structural_frame", "label": "Insp. Structural Frame", "type": "dropdown"},
            {"key": "insp_padeyes", "label": "Insp. PadEyes - Lifting Point", "type": "dropdown"},
            {"key": "insp_roof_floor", "label": "Insp. Roof/Floor Panels", "type": "dropdown"},
            {"key": "insp_doors", "label": "Insp. Doors", "type": "dropdown"},
            {"key": "check_marking", "label": "Check Marking Mandatory DataPlate", "type": "dropdown"},
            {"key": "nota_privata", "label": "Nota Privata", "type": "textarea"},
        ],
        "right_fields": _right_common(competent_person=True, schedule=True),
        "photo_slots": 4,
        "equipment_table": True,
    },

    "Workorder": {
        "title": "WORKORDER",
        "left_fields": [
            {"key": "customer", "label": "Customer", "type": "dropdown"},
            {"key": "data", "label": "Data", "type": "date"},
            {"key": "description", "label": "Description", "type": "textarea"},
        ],
        "right_fields": [],
        "photo_slots": 0,
        "equipment_table": False,
        "is_list_only": True,  # e' un elenco di riferimento (WO), non una scheda tecnica NDT
    },
}


def _tubular_schema(title, extra_left_top, table_columns):
    return {
        "title": title,
        "left_fields": extra_left_top + [
            {"key": "grade_steel", "label": "Grade Steel", "type": "text"},
            {"key": "weight", "label": "Weight", "type": "text"},
            {"key": "standard_of_inspection", "label": "Standard of Inspection", "type": "dropdown_free"},
            {"key": "comments", "label": "Comments", "type": "textarea"},
            {"key": "procedure", "label": "Procedure", "type": "text"},
            {"key": "type_of_inspection", "label": "Type of Inspection", "type": "text"},
            {"key": "nota_privata", "label": "Nota Privata", "type": "textarea"},
        ] + _mag_particle_block(),
        "right_fields": [
            {"key": "tool_description", "label": "Tool Description", "type": "text"},
        ] + _right_common(well_rig=True, extra_bottom=[
            {"key": "data_report_end", "label": "Data Report End", "type": "date"},
        ]),
        "photo_slots": 0,
        "equipment_table": True,
        "detail_table": {"label": "Dettaglio tubolari", "columns": table_columns},
    }


FORM_SCHEMAS["DrillPipe"] = _tubular_schema(
    "DRILLPIPE",
    [
        {"key": "od_size_nominal", "label": "OD Size Nominal", "type": "text"},
        {"key": "tool_joint_od_nominal", "label": "Tool Joint OD Nominal", "type": "text"},
        {"key": "id_nominal", "label": "ID Nominal", "type": "text"},
        {"key": "tool_joint_id_nominal", "label": "Tool Joint ID Nominal", "type": "text"},
        {"key": "wall_nominal", "label": "Wall Nominal", "type": "text"},
        {"key": "range_", "label": "Range", "type": "text"},
        {"key": "connection_thread", "label": "Connection Thread", "type": "dropdown"},
    ],
    ["Serial_Number", "Trace", "Tally", "Wall_Minimum", "Class", "Internal_Coating",
     "MPI_UpSet", "UT_UpSet", "EMI_Unit", "OD_Gage", "Tube_Condition", "PIN_ID", "PIN_OD",
     "PIN_DIMENSIONAL_2", "PIN_HB", "PIN_Tong_Space", "PIN_Thread_Condition", "BOX_OD"],
)

FORM_SCHEMAS["DrillCollar"] = _tubular_schema(
    "DRILLCOLLAR",
    [
        {"key": "od_size_nominal", "label": "OD Size Nominal", "type": "text"},
        {"key": "body_type", "label": "Body Type", "type": "text"},
        {"key": "connection_thread", "label": "Connection Thread", "type": "dropdown"},
        {"key": "range_", "label": "Range", "type": "text"},
        {"key": "id_nominal", "label": "ID Nominal", "type": "text"},
    ],
    ["Serial_Number", "Tally", "Elevator_Recess", "Slip_Recess", "Body_Condition",
     "PIN_OD", "PIN_ID", "PIN_Bevel", "PIN_SRG", "PIN_Conn_Leng", "PIN_Tong_Space",
     "PIN_DIMENSIONAL_3", "PIN_Thread_Condition", "PIN_HB", "BOX_OD"],
)

FORM_SCHEMAS["HWDP"] = _tubular_schema(
    "HWDP",
    [
        {"key": "od_size_nominal", "label": "OD Size Nominal", "type": "text"},
        {"key": "tool_joint_od_nominal", "label": "Tool Joint OD Nominal", "type": "text"},
        {"key": "wearpade_type", "label": "Wearpade Type", "type": "text"},
        {"key": "tool_joint_id_nominal", "label": "Tool Joint ID Nominal", "type": "text"},
        {"key": "wall_nominal", "label": "Wall Nominal", "type": "text"},
        {"key": "range_", "label": "Range", "type": "text"},
        {"key": "connection_thread", "label": "Connection Thread", "type": "dropdown"},
    ],
    ["Serial_Number", "Tally", "Wearpad", "Internal_Coating", "MPI_UpSet", "Tube_Condition",
     "PIN_ID", "PIN_OD", "PIN_DIMENSIONAL_3", "PIN_HB", "PIN_Tong_Space", "PIN_Thread_Condition",
     "BOX_OD", "BOX_DIMENSIONAL_3", "BOX_HB", "BOX_HEAT_Checking", "BOX_Tong_Space"],
)


def get_schema(mask_type):
    return FORM_SCHEMAS[mask_type]


def get_all_dropdown_fields():
    """Raccoglie tutti i campi a tendina di tutte le maschere (deduplicati per chiave),
    usati per popolare la sezione Amministrazione > Parametri."""
    found = {}
    for schema in FORM_SCHEMAS.values():
        for field in schema.get("left_fields", []) + schema.get("right_fields", []):
            if field["type"] in ("dropdown", "dropdown_free"):
                key = field.get("field_key", field["key"])
                if key not in found:
                    found[key] = field["label"]
    return dict(sorted(found.items(), key=lambda kv: kv[1]))
