"""
DECRIPTION:
    collection of functions to assist with handling Django forms

AUTHOR:
    David Slusser

REVISION:
    0.0.1
"""

# import system modules
import re 



def addFormAttributes(fields, attr_dict):
    """ 
    Description:
        Adds attributes to form fields
    
    Parameters:
        fields    - object of form fields
        attr_dict - dictionary of attributes 
                    ex.  {"_all_" : {"class" : "form-control"},
                          "name" : {"placeholder" : "cpetools"},
                         }
    """
    for field_name in fields:
        field = fields.get(field_name)
        d = {}
        if field:
            for k, v in attr_dict.iteritems():
                for k2, v2 in v.iteritems():
                    if (k == "_all_") or (k == field_name):
                        d.update({k2:v2})
        if d: 
            field.widget.attrs.update(d)
    return


def validateRegex(data, patterns, err_msg=None):
    """ 
    Description:
        Validates fields against regex patterns 
    
    Parameters:
        data     - object containing cleaned data
        patterns - dictionary containing form fields and regex patterns {field:pattern}
        err_msg  - error message to display on field
    
    Returns:
        dictionary containing error for fields that failed validation    
    """
    error_dict = {}
    if err_msg == None:
        err_msg = "Invalid value"
    for k,v in patterns.iteritems():           
        if not data.get(k) or data.get(k) == 'None':
            continue
        if not re.search(v, str(data.get(k))):
            error_dict[k] = [err_msg,]
    return error_dict


def verifyDropdownSelected(data, field, err_list=[], err_msg=None):
    """ 
    Description:
        Verify a dropdown element has a valid selection
    
    Parameters:
        data     - object containing cleaned data
        field    - form field to check
        err_list - list of values to interpret as invalid
        err_msg  - error message to display on field
    
    Returns:
        dictionary containing error for fields that failed validation
    """
    error_dict = {}
    if err_msg == None:
        err_msg = "This field is required"
    if not err_list:
        err_list = [None, "None", "---"]
    field_value = data.get(field)
    if not field_value or field_value in err_list:
        error_dict[field] = [err_msg]
    return error_dict


def verifyUnique(model, model_field, form_data, form_field, err_msg=None):
    """
    Description:
        Verify value doesn't already exist in db 
    
    Parameters:
        model       - model object
        model_field - field name in the model
        form_data   - form object's cleaned_data
        form_field  - field name in the form
        err_msg     - error message to display on field
    
    Returns:
        dictionary of errors {form_field: error_message}
    """
    error_dict = {}
    if err_msg == None:
        err_msg = "Value already exists"
    field_value = form_data.get(form_field)
    if field_value:
        queryset = model.objects.filter(**{model_field:field_value})
        if queryset:
            error_dict[form_field] = [err_msg]
    return error_dict
    
  

