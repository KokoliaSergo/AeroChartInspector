import uuid

ERROR_TYPES = [
    "Text", "Altitude", "Frequency", "Navaid", "Course / Bearing", 
    "Distance", "Speed", "Procedure", "Route", "Waypoint", 
    "Runway", "Aerodrome", "Obstacle", "Terrain", "Symbol", 
    "Geometry / Position", "Missing Information", "Incorrect Information", 
    "Formatting / Presentation", "Other"
]

SEVERITY_LEVELS = ["Critical", "Major", "Minor", "Observation"]

class ErrorItem:
    def __init__(self, error_id, err_type, description, chart="Updated chart", severity="Major", comments=""):
        self.id = error_id
        self.type = err_type
        self.description = description
        self.chart = chart
        self.severity = severity
        self.comments = comments