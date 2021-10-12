from watchmen.common.security.algorithm import algorithm_aes, algorithm_md5, algorithm_mask_mail, algorithm_mask_center

AES256_PKCS5_PADDING = 'AES256-PKCS5-PADDING'
MD5 = 'MD5'
SHA256 = 'SHA256'
MASK_MAIL = 'MASK-MAIL'
MASK_CENTER_3 = 'MASK-CENTER-3'
MASK_CENTER_5 = 'MASK-CENTER-5'
MASK_LAST_3 = 'MASK-LAST-3'
MASK_LAST_6 = 'MASK-LAST-6'
MASK_DAY = 'MASK-DAY'
MASK_MONTH = 'MASK-MONTH'
MASK_MONTH_DAY = 'MASK-MONTH-DAY'


def find_algorithm_encryption(factor_type,factor_encrypt):
    if factor_encrypt==AES256_PKCS5_PADDING:
        return algorithm_aes.encrypt
    elif factor_encrypt ==MD5:
        return algorithm_md5.encrypt
    elif factor_encrypt == SHA256:
        return algorithm_md5.encrypt
    elif factor_encrypt == MASK_MAIL:
        return algorithm_mask_mail.encrypt
    elif factor_encrypt ==MASK_CENTER_3:
        return algorithm_mask_center.encrypt
    elif factor_encrypt== MASK_CENTER_5:
        return algorithm_mask_center.encrypt
    else:
        raise NotImplementedError("not supported now")
