translate_distance_dict = {
    'sprint': 'спринт',
    'supersprint': 'суперспринт',
    'ironman': 'железная',
    'halfironman': 'полужелезная',
    'olympic': 'олимпийская',
    'halfmarathon': 'полумарафон',
    'marathon': 'марафон'
}

translate_month_dict = {
    'January': 'Января',
    'February': 'Февраля',
    'March': 'Марта',
    'April': 'Апреля',
    'May': 'Мая',
    'June': 'Июня',
    'July': 'Июля',
    'August': 'Августа',
    'September' : 'Сентября',
    'October': 'Октября',
    'November': 'Ноября',
    'December': 'Декабря'
}

def distance_to_russian(d):
    return translate_distance_dict.get(d) or d


def translate_month(m):
    return translate_month_dict[m]
