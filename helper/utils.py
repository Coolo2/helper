
def remove_numbers_from_string(string : str):
    return ''.join([i for i in string if not i.isdigit()])

def category_name_from_cog_name(cog_name : str):
    category_name = remove_numbers_from_string(cog_name).replace("cogs.", "")
    if "_" in category_name:
        category_name = category_name.split("_")[0]
    
    return category_name