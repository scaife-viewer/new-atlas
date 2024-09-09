from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def query(context, **kwargs):
    q = context["request"].GET.copy()
    for k, v in kwargs.items():
        if v:
            q[k] = v
        elif k in q:
            del q[k]
    return q.urlencode()
