from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Collection, Movie
from django.core.exceptions import ValidationError
from uuid import UUID

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    Allows users to register by providing a username and password.
    """
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password')

    def create(self, validated_data):
        """
        Create a new user instance with the validated data.

        Parameters:
        - validated_data (dict): Validated data containing username and password.

        Returns:
        - User: Newly created user instance.
        """
        user = User.objects.create_user(**validated_data)
        return user
    
class MovieSerializer(serializers.ModelSerializer):
    """
    Serializer for the Movie model.

    Serializes movie data including title, description, genres, and UUID.
    """
    class Meta:
        model = Movie
        fields = ['title', 'description', 'genres', 'uuid']

class CollectionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Collection model.

    Serializes collection data including title, UUID, description, and nested movies.
    """
    movies = MovieSerializer(many=True)  # Nested serializer for movies
    class Meta:
        model = Collection
        fields = ['title', 'uuid', 'description', 'movies']

    def create(self, validated_data):
        """
        Create a new collection instance with the validated data.
        Also create movie instances with the movie details supplied after validating.

        Parameters:
        - validated_data (dict): Validated data containing collection details and nested movies.

        Returns:
        - Collection: Newly created collection instance.
        """
        movies_data = validated_data.pop('movies')
        collection = Collection.objects.create(**validated_data)
        
        movie_objects = []
        errors = {}
        for index, movie_data in enumerate(movies_data, start=1):
            movie_serializer = MovieSerializer(data=movie_data)

            title = movie_data.get('title')
            
            if movie_serializer.is_valid():
                movie_objects.append(Movie(collection=collection, **movie_serializer.validated_data))
            else:
                errors[f'Movie {index}'] = {'errors': movie_serializer.errors, 'title': title}
        
        if errors:
            raise ValidationError(errors)
        
        Movie.objects.bulk_create(movie_objects)
        return collection

class CollectionListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing collections.

    Serializes collection data including title, UUID, and description.
    """
    class Meta:
        model = Collection
        fields = ['title', 'uuid', 'description']

class CollectionDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed view of a collection.

    Serializes collection data including title, description, and nested movies.
    """
    movies = MovieSerializer(many=True)

    class Meta:
        model = Collection
        fields = ['title', 'description', 'movies']


class CollectionUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating a collection.

    Serializes updated collection data including title, description, and nested movies.
    """
    movies = MovieSerializer(many=True)
    
    class Meta:
        model = Collection
        fields = ['title', 'description', 'movies']

    def validate(self, attrs):
        """
        Validate the data before updating the collection.

        Parameters:
        - attrs (dict): Dictionary containing updated collection data.

        Returns:
        - dict: Validated data.
        """
        movies_data = attrs.get('movies', [])
        for movie_data in movies_data:
            uuid_str = movie_data.get('uuid')
            if not uuid_str:
                raise ValidationError({'uuid': 'UUID is required for each movie.'})
            try:
                UUID(str(uuid_str))                
            except ValueError:
                raise ValidationError({'uuid': f'Invalid UUID format: {uuid_str}'})

        return attrs
    
    def update(self, instance, validated_data):
        """
        Update the collection instance with the validated data.

        Parameters:
        - instance (Collection): Collection instance to be updated.
        - validated_data (dict): Validated data containing updated collection details.

        Returns:
        - Collection: Updated collection instance.
        """
        movies_data = validated_data.pop('movies', [])
        instance = super().update(instance, validated_data)
        
        for movie_data in movies_data:
           movie_instance, _ = Movie.objects.update_or_create(collection=instance, uuid=movie_data.get('uuid'), defaults=movie_data)
        
        return instance
