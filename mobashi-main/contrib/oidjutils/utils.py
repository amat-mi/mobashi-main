from io import BytesIO
from django.urls import reverse
from django.core.cache import cache
import qrcode


# Added support for "want_no_link"
def field_link(obj, field=None, target=None, textfield=None, want_no_link=False):
    if obj.pk:
        if field:  # if requested
            # build link for an object pointed to the specified field, instead
            obj = getattr(obj, field)
        link = reverse(
            'admin:' + '_'.join([obj._meta.app_label, obj._meta.model_name, 'change']), args=(obj.pk,)
        )
        target = f' target="{target}"' if target else ''
        text = getattr(obj, textfield, 'Modifica')
        if callable(text):
            text = text()
        return text if want_no_link else f'<a href="{link}"{target}>{text}</a>'
    return ''


def build_qrcode(key, box_size=2, border=4, error_correction='M', output_format='PNG', use_cache=True):
    if key is None or key == '':
        raise ValueError('Missing key parameter')

    try:
        box_size = int(box_size)
    except:
        box_size = 2
    if box_size < 1 or box_size > 20:
        box_size = 2

    try:
        border = int(border)
    except:
        border = 4
    if border < 1 or border > 20:
        border = 4

    ecs = {'L': 1,
           'M': 0,
           'Q': 3,
           'H': 2, }
    try:
        error_correction = ecs[error_correction]
    except:
        error_correction = 0

    output_format = output_format if output_format in ['PNG', 'JPG'] else 'PNG'

    if use_cache:
        cache_key = u"qrcode_bs{}_bd{}_ec{}:{}".format(
            box_size, border, error_correction, key)
        res = cache.get(cache_key)
    if not res:
        img = qrcode.make(key,
                          box_size=box_size,
                          border=border,
                          error_correction=error_correction)
        output = BytesIO()
        img.save(output, output_format)
        res = output.getvalue()
        if use_cache:
            cache.set(cache_key, res, 60*60)
    return res
