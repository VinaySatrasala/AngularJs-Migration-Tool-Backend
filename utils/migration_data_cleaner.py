def clean_migration_data(data):
    """
    Recursively clean migration data by removing unnecessary metadata from folder entries.
    
    Args:
        data (dict): The migration data dictionary to clean
    
    Returns:
        dict: Cleaned migration data with folder metadata removed
    """
    def clean_node(node):
        # If node is not a dictionary, return it as is
        if not isinstance(node, dict):
            return node
        
        # Create a copy of the node to avoid modifying the original
        cleaned_node = {}
        
        # List of keys to preserve if they exist for folders
        folder_allowed_keys = ['public', 'src', 'components', 'services', 'directives', 'styles']
        
        for key, value in node.items():
            # If value is a dictionary and looks like a folder
            if isinstance(value, dict):
                # Check if this is a file entry (has specific file metadata)
                if any(k in value for k in ['file_name', 'file_type', 'relative_path']):
                    # This is a file entry, keep all its metadata
                    cleaned_node[key] = value
                elif key in folder_allowed_keys or key == 'files':
                    # This is a folder, recursively clean its contents
                    cleaned_node[key] = clean_node(value)
            else:
                # For non-dictionary values, keep them as is
                cleaned_node[key] = value
        
        return cleaned_node
    
    # Clean the entire data structure
    return clean_node(data)

class MigrationDataProcessor:
    def __init__(self, migration_data):
        """
        Initialize the Migration Data Processor
        
        Args:
            migration_data (dict): The original migration data
        """
        self.original_data = migration_data
        self.migration_data = clean_migration_data(migration_data)
    
    def get_cleaned_data(self):
        """
        Return the cleaned migration data
        
        Returns:
            dict: Cleaned migration data
        """
        return self.migration_data
    
    def restore_original_data(self):
        """
        Restore the original migration data
        
        Returns:
            dict: Original migration data
        """
        return self.original_data

# Example usage
# processor = MigrationDataProcessor(your_migration_data)
# cleaned_data = processor.get_cleaned_data()