def bytes_to_unicode(data):
        return data.decode("UTF-8")


def unicode_to_bytes(data):
    return data.encode("UTF-8")


def pretty_print(user, msg_type, destination, message):
    if isinstance(message, list):
        message = " ".join(message)
    print("%s %s %s :%s" % (user, msg_type, destination, message))
