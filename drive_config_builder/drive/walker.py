from drive.drive_reader import list_children, is_folder, get_file_url

def build_tree(drive_service, root_folder_id):
    '''
    Recursively builds a nested dictionary structure that mirrros the Google Drive folder hierarchy.
    
    :param drive_service: Authenticated Drive service object
    :param root_folder_id: ID of the root folder to start building the tree from
    :return: Nested python dictionary representing the folder structure ready to be serialized to JSON
    '''
    def walk(folder_id):
        children = list_children(drive_service, folder_id)
        node = {}
        for item in children:
            item_id = item['id']
            item_name = item['name']
            print(f"Processing item: {item_name} (ID: {item_id})")
            if is_folder(item):
                node[item_name] = walk(item_id)
            else:
                node[item_name] = get_file_url(item_id)
        
        return node
        
    
    
    return walk(root_folder_id)

