# pipeline/recall_categorizer.py
import re
from datetime import datetime




def format_recall_date(date_str):
    """Format recall date for display"""
    if date_str == 'Unknown' or not date_str or str(date_str).lower() == 'nan':
        return 'Date Unknown'
    
    try:
        # Try different date formats
        for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%Y-%m-%d %H:%M:%S', '%Y']:
            try:
                date_obj = datetime.strptime(str(date_str), fmt)
                return date_obj.strftime('%B %d, %Y')
            except ValueError:
                continue
        return str(date_str)  
    except:
        return str(date_str)

def categorize_recall(component, summary="", nhtsa_id=""):
    """
    Categorize recalls based on component and summary information
    Returns a clean category name for display
    """
    component = str(component).upper()
    summary = str(summary).upper()
    
    # Windshield-related categorization
    if 'WINDSHIELD' in component:
        if 'WIPER' in component:
            if 'MOTOR' in component:
                return 'WINDSHIELD WIPER MOTOR'
            elif 'LINKAGE' in component or 'LINK' in component:
                return 'WINDSHIELD WIPER LINKAGE'
            else:
                return 'WINDSHIELD WIPER'
        elif 'DEFOG' in component or 'DEFROST' in component:
            return 'WINDSHIELD DEFROSTER'
        else:
            return 'WINDSHIELD'
    
    # Wiper-specific (not windshield)
    elif 'WIPER' in component:
        if 'MOTOR' in component:
            return 'WINDSHIELD WIPER MOTOR'
        elif 'ARM' in component:
            return 'WINDSHIELD WIPER ARM'
        elif 'BLADE' in component:
            return 'WINDSHIELD WIPER BLADE'
        else:
            return 'WINDSHIELD WIPER'
    
    # Seat belt specific categorization
    elif any(keyword in component for keyword in ['SEAT BELT', 'SEATBELT', 'BELT']):
        if 'PRETENSIONER' in component or 'PRETENSIONER' in summary:
            return 'SEAT BELT PRETENSIONER'
        elif 'ANCHOR' in component or 'ANCHORAGE' in component:
            return 'SEAT BELT ANCHORAGE'
        elif 'RETRACTOR' in component:
            return 'SEAT BELT RETRACTOR'
        else:
            return 'SEAT BELT SYSTEM'
    
    # Engine related
    elif any(keyword in component for keyword in ['ENGINE', 'MOTOR', 'CYLINDER']):
        if 'COOLING' in component:
            return 'ENGINE COOLING'
        elif 'OIL' in component:
            return 'ENGINE OIL SYSTEM'
        else:
            return 'ENGINE'
    
    # Brake related
    elif any(keyword in component for keyword in ['BRAKE', 'BRAKING']):
        if 'PAD' in component:
            return 'BRAKE PADS'
        elif 'FLUID' in component:
            return 'BRAKE FLUID'
        elif 'LINE' in component or 'HOSE' in component:
            return 'BRAKE LINES'
        else:
            return 'BRAKE SYSTEM'
    
    # Electrical
    elif any(keyword in component for keyword in ['ELECTRICAL', 'WIRING', 'BATTERY', 'ALTERNATOR']):
        return 'ELECTRICAL SYSTEM'
    
    # Fuel system
    elif any(keyword in component for keyword in ['FUEL', 'GAS', 'TANK']):
        return 'FUEL SYSTEM'
    
    # Steering
    elif any(keyword in component for keyword in ['STEERING', 'WHEEL']):
        return 'STEERING SYSTEM'
    
    # Airbag
    elif 'AIRBAG' in component or 'AIR BAG' in component:
        return 'AIRBAG SYSTEM'
    
    # Transmission
    elif any(keyword in component for keyword in ['TRANSMISSION', 'GEAR']):
        return 'TRANSMISSION'
    
    # Suspension
    elif any(keyword in component for keyword in ['SUSPENSION', 'SHOCK', 'STRUT']):
        return 'SUSPENSION SYSTEM'
    
    # Default: clean up the component name
    else:
        # Remove common prefixes and clean up
        cleaned = re.sub(r'^(VEHICLE|AUTO|CAR)\s*', '', component)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned if cleaned else 'OTHER COMPONENT'

def get_recall_severity(summary, component):
    """
    Determine recall severity based on keywords in summary
    Returns: 'HIGH', 'MEDIUM', 'LOW'
    """
    summary = str(summary).upper()
    component = str(component).upper()
    
    high_risk_keywords = [
        'CRASH', 'FIRE', 'EXPLOSION', 'DEATH', 'INJURY', 'FATAL',
        'BRAKE FAILURE', 'STEERING LOSS', 'AIRBAG DEPLOY',
        'FUEL LEAK', 'CARBON MONOXIDE', 'SEAT BELT', 'RESTRAINT'
    ]
    
    medium_risk_keywords = [
        'MALFUNCTION', 'FAILURE', 'DEFECT', 'UNSAFE',
        'VISIBILITY', 'IMPAIRED', 'REDUCED PERFORMANCE'
    ]
    
    if any(keyword in summary for keyword in high_risk_keywords):
        return 'HIGH'
    elif any(keyword in summary for keyword in medium_risk_keywords):
        return 'MEDIUM'
    else:
        return 'LOW'

def format_recall_for_display(doc):
    """
    Format a recall document for consistent display
    """
    content_lines = doc.page_content.split('\n')
    
    # Parse the structured content
    recall_info = {}
    for line in content_lines:
        if ':' in line:
            key, value = line.split(':', 1)
            recall_info[key.strip()] = value.strip()
    
    # Extract basic information
    nhtsa_id = recall_info.get('Recall ID', 'Unknown')
    manufacturer = recall_info.get('Manufacturer', 'Unknown')
    component = recall_info.get('Component', 'Unknown')
    summary = recall_info.get('Summary', 'No summary available')
    action = recall_info.get('Action', 'No action specified')
    recall_date = recall_info.get('Recall Date', doc.metadata.get('recall_date', 'Unknown'))
    
    # Format date for display
    formatted_date = format_recall_date(recall_date)
    
    # Get category and severity
    category = categorize_recall(component, summary, nhtsa_id)
    severity = get_recall_severity(summary, component)
    
    return {
        'nhtsa_id': nhtsa_id,
        'manufacturer': manufacturer,
        'component': component,
        'summary': summary,
        'action': action,
        'category': category,
        'severity': severity,
        'recall_date': recall_date,
        'formatted_date': formatted_date
    }