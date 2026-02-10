import graphene
from graphene import List, String, Argument
from models import UserType, User
import json 

# Security: Deny certain query keywords to prevent unauthorized access
REQUEST_KEYWORD_DENYLIST = ['is_admin', 'flag', '$where']

def object_contains_denylist_key(obj, denylist):
    """
    Check if the object contains any denylisted keyword.
    Note: This implementation skips __proto__ and constructor keys
    to avoid issues with prototype-like patterns in JSON data.
    """
    if not isinstance(obj, dict):
        return False
    
    for key, value in obj.items():
        # Skip prototype-related keys (common in JS data)
        if key in ('__proto__', 'constructor', 'prototype'):
            continue
        
        # Check if key is in denylist
        if key in denylist:
            return True
        
        # Recursively check nested objects
        if isinstance(value, dict):
            if object_contains_denylist_key(value, denylist):
                return True
        elif isinstance(value, list):
            for item in value:
                if object_contains_denylist_key(item, denylist):
                    return True
    
    return False

def expand_result_on_key_path(obj):
    """
    Process the object and expand any prototype-like key paths.
    This handles __proto__ and constructor.prototype patterns
    by merging their contents into the result object.
    
    Note: This is similar to how Parse Server's DatabaseController
    handles object expansion in _expandResultOnKeyPath method.
    """
    if not isinstance(obj, dict):
        return obj
    
    result = {}
    
    for key, value in obj.items():
        if key == '__proto__' and isinstance(value, dict):
            # Expand __proto__ by merging its contents into result
            for proto_key, proto_value in value.items():
                result[proto_key] = proto_value
        elif key == 'constructor' and isinstance(value, dict):
            # Handle constructor.prototype pattern
            if 'prototype' in value and isinstance(value['prototype'], dict):
                for proto_key, proto_value in value['prototype'].items():
                    result[proto_key] = proto_value
        else:
            result[key] = value
    
    return result

class Query(graphene.ObjectType):
    users = List(UserType, search=Argument(String), options=Argument(String), dummy=Argument(String))

    def resolve_users(self, info, search=None, options=None, dummy=None):
        query = User.objects()
 
        if search:
            try:
                search_criteria = json.loads(search)
                
                # Security check: Reject queries with denylisted keywords
                if object_contains_denylist_key(search_criteria, REQUEST_KEYWORD_DENYLIST):
                    raise ValueError("Query contains restricted keywords")
                
                # Process and expand the search criteria (handles prototype patterns)
                expanded_criteria = expand_result_on_key_path(search_criteria)
                
                query = query.filter(**expanded_criteria)
            except json.JSONDecodeError:
                pass
            except ValueError as e:
                # Return empty result on security violation
                return []
 
        if options:
            try:
                options_criteria = json.loads(options)
                if 'skip' in options_criteria:
                    query = query.skip(options_criteria['skip'])
                if 'limit' in options_criteria:
                    query = query.limit(options_criteria['limit'])
            except json.JSONDecodeError:
                pass  

        return query

schema = graphene.Schema(query=Query)
