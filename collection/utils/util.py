import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

def create_retry_session(retries=5, backoff_factor=0.3, status_forcelist=(500, 502, 504)):
    """
    Create a session with retry functionality.

    This function creates a requests Session object with retry functionality for handling
    transient errors like connection timeouts and server errors.

    Parameters:
        retries (int): The maximum number of retries for each request (default is 5).
        backoff_factor (float): The backoff factor for exponential backoff between retries
            (default is 0.3).
        status_forcelist (tuple): A tuple of HTTP status codes that will trigger a retry
            (default is (500, 502, 504)).

    Returns:
        requests.Session: A requests Session object configured with retry functionality.
    """
    session = requests.Session()
    retry = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


