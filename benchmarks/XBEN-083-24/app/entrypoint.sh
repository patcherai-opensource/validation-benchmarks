#!/bin/bash

# Set default values for environment variables if not provided
FLAG=${FLAG:-"FLAG{placeholder}"}

# Export FLAG so PHP can access it via getenv()
export FLAG

echo "BuildFlow CI starting..."
echo "Environment configured."

# Start Apache in the foreground
apache2-foreground
