from django import template
register = template.Library()

#Access contents of dynamically-created variables
@register.simple_tag(takes_context=True)
def dynamicVariableValue(context, DynamicVariableName):
    #Returns value of DynamicVariableName into the context
    return context.get(DynamicVariableName, None)

#Access the media type of an instance in a combined queryset of all media types
@register.filter
def classname(obj):
    return obj.__class__.__name__

#Separating URL parameters and reassembling relative to the current page
#eg: page=2 and title="her" allowing both filtering and pagination
@register.simple_tag
def relativeUrl(value, field_name, urlencode=None):
    url = '?{}={}'.format(field_name, value)
    if urlencode:
        querystring = urlencode.split('&')
        filtered_querystring = filter(lambda p: p.split('=')[0] != field_name, querystring)
        encoded_querystring = '&'.join(filtered_querystring)
        url = '{}&{}'.format(url, encoded_querystring)
    return url