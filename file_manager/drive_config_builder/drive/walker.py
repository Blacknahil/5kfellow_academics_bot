from .drive_reader import list_children, is_folder, get_file_url


def _normalize_item_name(name, folder):
    """Trim all names; additionally lowercase folder names for stable navigation keys."""
    cleaned_name = str(name).strip()
    return cleaned_name.lower() if folder else cleaned_name

def build_tree(drive_service, root_folder_id):
    '''
    Recursively builds a nested dictionary structure that mirrors the Google Drive folder hierarchy.
    
    :param drive_service: Authenticated Drive service object
    :param root_folder_id: ID of the root folder to start building the tree from
    :return: Nested python dictionary representing the folder structure ready to be serialized to JSON
    '''
    def walk(folder_id):
        children = list_children(drive_service, folder_id)
        node = {}
        for item in children:
            item_id = item['id']
            folder = is_folder(item)
            item_name = _normalize_item_name(item.get('name', ''), folder)
            print(f"Processing item: {item_name} (ID: {item_id})")
            if folder:
                node[item_name] = walk(item_id)
            else:
                node[item_name] = item_id
        
        return node
        
    
    
    return walk(root_folder_id)

