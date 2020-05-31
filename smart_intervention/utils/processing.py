def mass_process(callback):
    """
    A decorator which
    :return:
    """
    to_process, processor = callback()
    for element in to_process:
        processor(element)
