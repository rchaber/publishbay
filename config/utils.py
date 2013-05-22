

def split_3cols(l):
    result = {}
    last_len = int(round(len(l)/3))
    if len(l) % 3 == 0:
        result['left'] = l[0:len(l)/3]
        result['center'] = l[len(l)/3:(len(l)/3)*2]
        result['right'] = l[-len(l)/3:]
    elif len(l) % 3 == 1:
        result['left'] = l[0:(len(l)-last_len)/2+1]
        result['center'] = l[(len(l)-last_len)/2+1:len(l)-last_len]
        result['right'] = l[-last_len:]
    else:
        result['left'] = l[0:(len(l)-last_len)/2]
        result['center'] = l[(len(l)-last_len)/2:len(l)-last_len]
        result['right'] = l[-last_len:]
    return result


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


joblist = ['Publisher',
           'Manager',
           'Editor',
           'Professional Reader',
           'Designer',
           'Translator',
           'Proofreader']

genres_fiction = ['Action and Adventure',
                  'Chick Lit',
                  'Children',
                  'Commercial Fiction',
                  'Contemporary',
                  'Crime',
                  'Erotica',
                  'Family Saga',
                  'Fantasy',
                  'Dark Fantasy',
                  'Gay and Lesbian',
                  'General Fiction',
                  'Graphic Novels',
                  'Historical Fiction',
                  'Horror',
                  'Humour',
                  'Literary Fiction',
                  'Military and Espionage',
                  'Multicultural',
                  'Mystery',
                  'Offbeat or Quirky',
                  'Picture Books',
                  'Religious and Inspirational',
                  'Romance',
                  'Science Fiction',
                  'Short Story Collections',
                  'Thrillers and Suspense',
                  'Western',
                  "Women's Fiction",
                  'Young Adult']

genres_nonfiction = ['Art & Photography',
                     'Biography & Memoirs',
                     'Business & Finance',
                     'Celebrity & Pop Culture',
                     'Music, Film & Entertainment',
                     'Cookbooks',
                     'Cultural/Social Issues',
                     'Current Affairs & Politics',
                     'Food & Lifestyle',
                     'Gardening',
                     'Gay & Lesbian',
                     'General Non-Fiction',
                     'History & Military',
                     'Home Decorating & Design',
                     'How To',
                     'Humour & Gift Books',
                     'Journalism',
                     'Juvenile',
                     'Medical, Health & Fitness',
                     'Multicultural',
                     'Narrative',
                     'Nature & Ecology',
                     'Parenting',
                     'Pets',
                     'Psychology',
                     'Reference',
                     'Relationship & Dating',
                     'Religion & Spirituality',
                     'Science & Technology',
                     'Self-Help',
                     'Sports',
                     'Travel',
                     'True Adventure & True Crime',
                     'Women Issues']
