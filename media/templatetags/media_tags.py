from django import template
register = template.Library()

@register.simple_tag(takes_context=True)
def dynamicVariableValue(context, DynamicVariableName):
    """ Returns value of DynamicVariableName into the context """
    return context.get(DynamicVariableName, None)