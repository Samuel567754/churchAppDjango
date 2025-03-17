from django.core.signing import TimestampSigner
from django.urls import reverse

def generate_action_link(request, member, action):
    signer = TimestampSigner()
    # Create a token in the format "member_id:action"
    token = signer.sign(f"{member.pk}:{action}")
    # Generate the URL for our custom view
    url = request.build_absolute_uri(reverse('account:member-action', kwargs={'token': token}))
    return url
