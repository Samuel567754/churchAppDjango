# church/context_processors.py
from .models import Church

def church_info(request):
    """
    Returns the church instance to be used in the site's templates.
    Adjust this logic if you have multiple church records.
    """
    # For instance, if you only expect one church record:
    church = Church.objects.first()
    
    # Alternatively, to return all churches:
    # churches = Church.objects.all()
    # return {'churches': churches}
    
    return {'church': church}