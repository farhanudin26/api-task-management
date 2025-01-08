def get_total_pages(size, count):
    extra_page = 1 if size is not None and count % size > 0 else 0
    total_pages = (count // size) + extra_page if size is not None else None
    return total_pages