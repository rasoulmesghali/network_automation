import re
mask_regex = "^(((255\.){3}(255|254|252|248|240|224|192|128|0+))|((255\.){2}(255|254|252|248|240|224|192|128|0+)\.0)|((255\.)(255|254|252|248|240|224|192|128|0+)(\.0+){2})|((255|254|252|248|240|224|192|128|0+)(\.0+){3}))$"

def validate_subnetmaskv4(mask):
    """
    This function validates the mask comming from user input parameters 
    """
    
    if(re.search(mask_regex, mask)):
        return True        
    return False