def mass_process(callback):
    """
    A decorator which
    :return:
    """

    def wrapper(*args, **kwargs):
        to_process, processor = callback(*args, **kwargs)
        for element in to_process:
            processor(element)

    return wrapper
