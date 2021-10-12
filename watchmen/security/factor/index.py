def is_security_scope(factor_type: str):
    return factor_type in ["phone", "mobile", "fax", "email", "id-no", "date-of-birth"]
