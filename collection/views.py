from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegistrationSerializer
import requests
from django.contrib.auth import authenticate
from .utils.util import create_retry_session
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Collection, Movie, RequestCounter
from .serializers import CollectionSerializer, CollectionListSerializer, CollectionDetailSerializer, CollectionUpdateSerializer
import os
from uuid import UUID

@api_view(['POST'])
@authentication_classes([])
def register(request):
    """
    Handle user registration.

    Allows users to register by providing a username and password.

    POST /register/

    Parameters:
    - request (HttpRequest): HTTP request containing user registration data.
    
    Request Payload:
        {
            “username”: <desired username>,
            “password”: <desired password>
        }

    Returns:
    - Response: HTTP response containing access token on successful registration,
                or error response with status code 400 if registration fails.
    
    Response:
        {
            “access_token”: <Access Token>
        }
    """
    if request.method == 'POST':
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({'access_token': str(refresh.access_token)}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
@authentication_classes([])
def login(request):
    """
    Handle user login.

    Allows users to login by providing a username and password.

    POST /login/

    Parameters:
    - request (HttpRequest): HTTP request containing user login data.

    Request Payload:
        {
            “username”: <desired username>,
            “password”: <desired password>
        }

    Returns:
    - Response: HTTP response containing access token on successful login,
                or error response with status code 401 if login fails.

    Response:
        {
            “access_token”: <Access Token>
        }
    
    """
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response({'access_token': str(refresh.access_token)}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_movies(request):
    """
    Retrieve paginated list of movies from a third-party API.

    Makes a request to a third-party API to retrieve a paginated list of movies.
    The data is then returned in the API response.
    Since the third-party API is flaky, the request is retried 5 times usin retry session.

    GET /movies/

    Parameters:
    - request (HttpRequest): HTTP request.

    Returns:
    - Response: HTTP response containing paginated list of movies,
                or error response with status code 500 if an error occurs.
    """
    base_url = "https://demo.credy.in/api/v1/maya/movies/"
    username = os.getenv('USER_NAME')
    password = os.getenv('PASS_WORD')

    try:
        session = create_retry_session()
        page_number = request.query_params.get('page', 1)
        url = f"{base_url}?page={page_number}"
        response = session.get(url, auth=(username, password))
        response.raise_for_status()  # Raise an exception for any HTTP errors

        data = response.json()
        data['data'] = data.pop('results', [])

        if data['next']:
            data['next'] = request.build_absolute_uri(f"{request.path}?page={int(page_number) + 1}")
        if data['previous']:
            data['previous'] = request.build_absolute_uri(f"{request.path}?page={int(page_number) - 1}")

        return Response(data)
    
    except requests.exceptions.RequestException as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CollectionListView(APIView):
    """
    API view for listing and creating collections.

    Allows users to list existing collections and create new collections for an authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Handle GET request for listing collections.

        GET /collection/

        Parameters:
        - request (HttpRequest): HTTP request.

        Returns:
        - Response: HTTP response containing serialized list of collections.
        """
        collections = Collection.objects.filter(user=request.user)
        serializer = CollectionListSerializer(collections, many=True, context={'request': request})
        user = request.user        
        movies = Movie.objects.filter(collection__user=user)
        genre_count = {}
        for movie in movies:
            for genre in movie.genres.split(','):
                genre_count[genre] = genre_count.get(genre, 0) + 1
        sorted_genres = sorted(genre_count.items(), key=lambda x: x[1], reverse=True)
        top_3_genres = [genre[0] for genre in sorted_genres[:3]] if len(sorted_genres) >= 3 else sorted_genres
        favourite_genres = ', '.join(top_3_genres) if top_3_genres else ""
    
        data = {
            'is_success': True,
            'data': {
                'collections': serializer.data,
                'favourite_genres': favourite_genres,
            }
        }
        return Response(data)

    def post(self, request):
        """
        Handle POST request for creating a new collection.

        POST /collection/

        Parameters:
        - request (HttpRequest): HTTP request containing data for creating a new collection.

        Request payload:
        {
            “title”: “<Title of the collection>”,
            “description”: “<Description of the collection>”,
            “movies”: [
                {
                    “title”: <title of the movie>,
                    “description”: <description of the movie>,
                    “genres”: <generes>,
                    “uuid”: <uuid>
                }, ...
            ]
        }

        Returns:
        - Response: HTTP response containing newly created collection data,
                    or error response with status code 400 if creation fails.

        Response payload:
        {
            “collection_uuid”: <uuid of the collection item>
        }
        """
        serializer = CollectionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({'collection_uuid': serializer.instance.uuid}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CollectionDetailView(APIView):
    """
    API view for retrieving, updating, and deleting collections.

    Allows users to retrieve, update, and delete collections by UUID.
    """
    permission_classes = [IsAuthenticated]

    def valid_uuid(self, uuid):
        """
        Validate a uuid string.

        Returns True if given uuid is valid.

        Returns False if given uuid is invalid.
        """
        try:
            uuid = UUID(uuid)
            return True
        except ValueError:
            return False

    def get(self, request, collection_uuid):
        """
        Handle GET request for retrieving a collection.

        GET /collection/<collection_uuid>/

        Parameters:
        - request (HttpRequest): HTTP request.
        - collection_uuid (str): UUID of the collection to retrieve.

        Returns:
        - Response: HTTP response containing serialized collection data,
                    or error response with status code 404 if collection does not exist.
        """
        if not self.valid_uuid(collection_uuid):
            return Response({"error": "Invalid UUID format."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            collection = Collection.objects.get(uuid=collection_uuid, user=request.user)
        except Collection.DoesNotExist:
            return Response({'error': 'Collection not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CollectionDetailSerializer(collection)
        return Response(serializer.data)

    def put(self, request, collection_uuid):
        """
        Handle PUT request for updating a collection.

        PUT /collection/<collection_uuid>/

        Parameters:
        - request (HttpRequest): HTTP request containing updated collection data.
        - collection_uuid (str): UUID of the collection to update.

        Request:
        {
            “title”: <Optional updated title>,
            “description”: <Optional updated description>,
            “movies”: <Optional movie list to be updated>,
        }

        Returns:
        - Response: HTTP response containing updated collection data,
                    or error response with status code 404 if collection does not exist.
        """
        if not self.valid_uuid(collection_uuid):
            return Response({"error": "Invalid UUID format."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            collection = Collection.objects.get(uuid=collection_uuid, user=request.user)
        except Collection.DoesNotExist:
            return Response({'error': 'Collection not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CollectionUpdateSerializer(collection, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, collection_uuid):
        """
        Handle DELETE request for deleting a collection.

        Parameters:
        - request (HttpRequest): HTTP request.
        - collection_uuid (str): UUID of the collection to delete.

        Returns:
        - Response: HTTP response with status code 204 if deletion is successful,
                    or error response with status code 404 if collection does not exist.
        """
        if not self.valid_uuid(collection_uuid):
            return Response({"error": "Invalid UUID format."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            collection = Collection.objects.get(uuid=collection_uuid, user=request.user)
        except Collection.DoesNotExist:
            return Response({'error': 'Collection not found'}, status=status.HTTP_404_NOT_FOUND)

        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class RequestCountView(APIView):
    """
    API view for retrieving the request count.

    Allows users to retrieve the total number of requests made to the server.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Handle GET request for retrieving the request count.

        Parameters:
        - request (HttpRequest): HTTP request.

        GET /request-count/

        Response:
        {
            “requests”: <number of requests served by this server till now>.
        }

        Returns:
        - Response: HTTP response containing the request count.
        """
        counter = RequestCounter.objects.first()
        return Response({'requests': counter.count}, status=status.HTTP_200_OK)

class ResetRequestCountView(APIView):
    """
    API view for resetting the request

    Allows users to reset the request count.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Handle POST request for resetting the request count.

        Parameters:
        - request (HttpRequest): HTTP request.       

        POST /request-count/reset/

        Response:
        {
            “message”: “request count reset successfully”
        }

        Returns:
        - Response: HTTP response containing the request count.
        """
 
        counter = RequestCounter.objects.first()
        counter.count = 0
        counter.save()
        return Response({'message': 'Request count reset successfully'}, status=status.HTTP_200_OK)