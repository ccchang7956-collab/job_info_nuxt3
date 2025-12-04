
from fastapi.templating import Jinja2Templates
from app.Utils.FormatUtils import format_place, format_roc_date, convert_to_gregorian_date_iso

# Initialize Jinja2Templates (async disabled for compatibility)
templates = Jinja2Templates(directory="templates", autoescape=True)

# Register custom filters
templates.env.filters["format_place"] = format_place
templates.env.filters["format_roc_date"] = format_roc_date
templates.env.filters["convert_to_gregorian_date_iso"] = convert_to_gregorian_date_iso
