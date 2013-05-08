
def pagination(number_of_pages, current_page, nav_len):  # better algorithm to paginate
    if nav_len > number_of_pages:
        nav_len = number_of_pages
    center = float(nav_len) / 2 + 1
    if current_page < center:
        nav_bar = [i for i in range(1, nav_len + 1)]
    elif current_page > number_of_pages - nav_len / 2:
        nav_bar = [i for i in range(number_of_pages - nav_len + 1, number_of_pages + 1)]
    else:
        start = current_page - nav_len / 2
        nav_bar = [i for i in range(start, start + nav_len)]
    active_mark = nav_bar.index(current_page)
    return nav_bar, active_mark
