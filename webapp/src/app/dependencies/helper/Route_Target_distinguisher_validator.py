
def validate_rt_rd(value):
    """
    This function validates the format of route target and route distinguisher
    """
    if not ":" in value:
        return False     
    lst = value.split(":")
    try:
        for i in lst:
            int(i)
    except:
        return False
    return True