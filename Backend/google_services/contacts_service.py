"""
Google Contacts Service (People API)
Integrates with People API for contact management
"""
from googleapiclient.discovery import build
from typing import Any, Optional


def get_people_service(credentials: Any):
    """Create People API service instance"""
    return build("people", "v1", credentials=credentials)


def list_contacts(credentials: Any, max_results: int = 100):
    """List all contacts"""
    service = get_people_service(credentials)
    
    results = service.people().connections().list(
        resourceName="people/me",
        pageSize=max_results,
        personFields="names,emailAddresses,phoneNumbers,organizations,photos,birthdays,addresses"
    ).execute()
    
    connections = results.get("connections", [])
    
    contacts = []
    for person in connections:
        contact = {
            "resourceName": person.get("resourceName"),
            "name": None,
            "emails": [],
            "phones": [],
            "organization": None,
            "photo": None,
        }
        
        names = person.get("names", [])
        if names:
            contact["name"] = names[0].get("displayName")
        
        emails = person.get("emailAddresses", [])
        contact["emails"] = [e.get("value") for e in emails]
        
        phones = person.get("phoneNumbers", [])
        contact["phones"] = [p.get("value") for p in phones]
        
        orgs = person.get("organizations", [])
        if orgs:
            contact["organization"] = orgs[0].get("name")
        
        photos = person.get("photos", [])
        if photos:
            contact["photo"] = photos[0].get("url")
        
        contacts.append(contact)
    
    return contacts


def get_contact(credentials: Any, resource_name: str):
    """Get a specific contact by resource name"""
    service = get_people_service(credentials)
    
    person = service.people().get(
        resourceName=resource_name,
        personFields="names,emailAddresses,phoneNumbers,organizations,photos,birthdays,addresses,biographies"
    ).execute()
    
    return person


def create_contact(credentials: Any, name: str, email: Optional[str] = None, phone: Optional[str] = None, organization: Optional[str] = None):
    """Create a new contact"""
    service = get_people_service(credentials)
    
    person = {
        "names": [{"givenName": name}]
    }
    
    if email:
        person["emailAddresses"] = [{"value": email}]
    
    if phone:
        person["phoneNumbers"] = [{"value": phone}]
    
    if organization:
        person["organizations"] = [{"name": organization}]
    
    result = service.people().createContact(body=person).execute()
    
    return {
        "resourceName": result.get("resourceName"),
        "name": name,
        "email": email,
        "phone": phone,
        "status": "created"
    }


def delete_contact(credentials: Any, resource_name: str):
    """Delete a contact"""
    service = get_people_service(credentials)
    service.people().deleteContact(resourceName=resource_name).execute()
    return {"message": "Contact deleted successfully"}


def search_contacts(credentials: Any, query: str, max_results: int = 10):
    """Search contacts by name or email"""
    service = get_people_service(credentials)
    
    results = service.people().searchContacts(
        query=query,
        pageSize=max_results,
        readMask="names,emailAddresses,phoneNumbers"
    ).execute()
    
    return results.get("results", [])


def get_other_contacts(credentials: Any, max_results: int = 100):
    """Get 'Other contacts' (auto-saved from emails)"""
    service = get_people_service(credentials)
    
    results = service.otherContacts().list(
        pageSize=max_results,
        readMask="names,emailAddresses"
    ).execute()
    
    return results.get("otherContacts", [])
