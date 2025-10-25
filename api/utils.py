"""
Utility functions for Finance AI API
"""
from datetime import datetime, date, time
from typing import Any, Dict
from enum import Enum

def date_to_datetime(date_obj: date) -> datetime:
    """Convert date to datetime for MongoDB compatibility"""
    if isinstance(date_obj, datetime):
        return date_obj
    return datetime.combine(date_obj, time.min)

def datetime_to_date(datetime_obj: datetime) -> date:
    """Convert datetime to date"""
    if isinstance(datetime_obj, date) and not isinstance(datetime_obj, datetime):
        return datetime_obj
    return datetime_obj.date()

def prepare_document_for_mongo(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare a document for MongoDB insertion by converting date objects to datetime"""
    prepared_doc = {}
    for key, value in doc.items():
        if isinstance(value, date) and not isinstance(value, datetime):
            # Convert date to datetime
            prepared_doc[key] = date_to_datetime(value)
        elif isinstance(value, Enum):
            # Convert enum to its value
            prepared_doc[key] = value.value
        elif isinstance(value, dict):
            # Recursively handle nested dictionaries
            prepared_doc[key] = prepare_document_for_mongo(value)
        elif isinstance(value, list):
            # Handle lists
            prepared_doc[key] = [
                prepare_document_for_mongo(item) if isinstance(item, dict) 
                else item.value if isinstance(item, Enum)
                else date_to_datetime(item) if isinstance(item, date) and not isinstance(item, datetime)
                else item
                for item in value
            ]
        else:
            prepared_doc[key] = value
    return prepared_doc

def prepare_date_range_for_mongo(start_date: date, end_date: date) -> Dict[str, datetime]:
    """Prepare date range for MongoDB queries"""
    return {
        "$gte": date_to_datetime(start_date),
        "$lte": datetime.combine(end_date, time.max)
    }

def prepare_document_for_vector_store(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare a document for vector store by converting complex types to simple types"""
    prepared_doc = {}
    for key, value in doc.items():
        if isinstance(value, (date, datetime)):
            # Convert dates/datetimes to ISO string
            if isinstance(value, date) and not isinstance(value, datetime):
                prepared_doc[key] = value.isoformat()
            else:
                prepared_doc[key] = value.isoformat()
        elif isinstance(value, Enum):
            # Convert enum to its value
            prepared_doc[key] = value.value
        elif isinstance(value, dict):
            # Recursively handle nested dictionaries
            prepared_doc[key] = prepare_document_for_vector_store(value)
        elif isinstance(value, list):
            # Handle lists
            prepared_doc[key] = [
                prepare_document_for_vector_store(item) if isinstance(item, dict) 
                else item.value if isinstance(item, Enum)
                else item.isoformat() if isinstance(item, (date, datetime))
                else item
                for item in value
            ]
        elif isinstance(value, (int, float, str, bool)) or value is None:
            # Keep simple types as is
            prepared_doc[key] = value
        else:
            # Convert other types to string
            prepared_doc[key] = str(value)
    return prepared_doc
