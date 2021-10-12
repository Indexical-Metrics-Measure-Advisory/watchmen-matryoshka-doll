def encrypt(value_, params):
    lo = value_.find("@")
    if lo > 0:
        return "#####" + value_[lo - 1:]
    else:
        raise Exception("invalid email {}".format(value_))
