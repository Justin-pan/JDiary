def get_page(total, page):
    show_page = 5
    offset = 2
    start = 1
    end = total

    if total > show_page:
        if page > offset:
            start = page - offset
            if total > page + offset:
                end = page + offset
            else:
                end = total
        else:
            start = 1
            if total > show_page:
                end = show_page
            else:
                end = total
        if page + offset > total:
            start = start - (page + offset - end)
        
    
    page_range = range(start, end + 1)
    return page_range