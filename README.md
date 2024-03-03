# Movie Collection App

Movie Collection App is a simple Django Rest Framework based application for creating and managing movie collections. It provides RESTful APIs for basic CRUD operations on collections and user authentication using JWT.

## Features

- User registration and authentication
- Create, read, update, and delete collections
- Add movies to collections

## Installation

To run the Movie Collection App locally, follow these steps:

1. Clone the repository:

    ```bash
    https://github.com/pankajpatil001/movie_collection_app.git
    ```

2. Navigate to the project directory:

    ```bash
    cd movie_collection_app
    ```

3. Install dependencies

    ```bash
    pip install -r requirements.txt
    ```

4. Apply migrations

    ```bash
    python manage.py makemigrations
    python manage.py migrate

5. Run the development server:

    ```bash
    python manage.py runserver

6. Access the application at <http://localhost:8000>

## Testing

The project includes unit tests for the API endpoints. To run the tests, use the following command:

```bash
    python manage.py test
```

## Usage

## API Endpoints

POST /register/: Create a new user account.

POST /login/: Log in to an existing user account.

GET /collection/: Retrieve all collections for an authenticated user.

POST /collection/: Create a collection for an authenticated user.

GET /collection/{collection_uuid}/: Retrieve a collection using its uuid.

PUT /collection/{collection_uuid}/: Update a collection using its uuid.

GET /request-count/: Get the current request count.

POST /request-count/reset/: Reset the request counter.

# API Documentation and Usage Examples

## Introduction

This document provides comprehensive documentation for the Movie Collection App API endpoints along with usage examples.

### Authentication

All endpoints require authentication using JWT Token authentication. You need to include the Authorization header in your requests with the value Bearer <your_token_here>.

## Endpoints

### Create a User Account

#### Endpoint

POST /register/

#### Description

Create a new user account.

#### Request Body

- username (string): The username for the new user.
- password (string): The password for the new user.

#### Example

```json
{
  "username": "testuser",
  "password": "password123"
}
```

#### Response

- Status Code: 201 CREATED

#### Response Body

```json
{
    "access_token": "<Access Token>"
}
```

### User Login

#### Endpoint

POST /login/

#### Description

Authenticate a user and get the jwt authentication token.

#### Request Body

- username (string): The username for the user.
- password (string): The password for the user.

#### Example

```json
{
  "username": "testuser",
  "password": "password123"
}
```

#### Response

- Status Code: 200 OK

#### Response Body

```json
{
    "access_token": "<Access Token>"
}
```

### Get all movies

#### Endpoint

GET /movies/

#### Example

```bash
GET /movies/
```

#### Description

Retrieve all movie details

#### Response Body

```json
{
    "count": "<total number of movies>",
    "next": "<link for next page, if present>",
    "previous": "<link for previous page>",
    "data": [
        {
            "title": "<title of the movie>",
            "description": "<a description of the movie>",
            "genres": "<a comma separated list of genres, if present>",
		    "uuid": "<a unique uuid for the movie>"
        }
    ]
}

```

### Get all collection with top 3 favourite genres

#### Endpoint

GET /collection/

#### Description

Retrieve all collection with top 3 favourite genres

#### Example

```bash
GET /collection/
```

#### Response Body

```json
{
    "is_success": true,
    "data": {
        "collections": [
            {
                "title": "<Title of my collection>",
                "uuid": "<uuid of the collection name>",
                "description": "My description of the collection."
            }
        ],
        "favourite_genres": "<My top 3 favorite genres based on the movies I have added in my collections>."
    }
}
```

### Create a collection with movies

#### Endpoint

POST /collection/

#### Description

Create a collection with movies

#### Example

```bash
POST /collection/
```

#### Request Body

```json
{
    "title": "<Title of the collection>",
    "description": "<Description of the collection>",
    "movies": [
        {
            "title": "<title of the movie>",
            "description": "<description of the movie>",
            "genres": "<generes>",
            "uuid": "<uuid>"
        }
    ]
}
```

#### Response Body

```json
{
    "collection_uuid": "<uuid of the collection item>"
}
```

### Get a collection

#### Endpoint

GET /collection/{collection_uuid}/

#### Description

Get a collection with a list of its movies

#### Parameters

- collection_uuid (UUID): The uuid of the collection.

#### Response

- Status Code: 200 OK

#### Response Body

```json
{
    "title": "<Title of the collection>",
    "description": "<Description of the collection>",
    "movies": "<Details of movies in my collection>"
}
```

### Update the movie list in a collection

#### Endpoint

GET /collection/{collection_uuid}/

#### Description

Update the movie list in a collection

#### Parameters

- collection_uuid (UUID): The uuid of the collection.

#### Response

- Status Code: 200 OK

#### Response Body

```json
{
    "title": "<Title of the collection>",
    "description": "<Description of the collection>",
    "movies": "<Details of movies in my collection>"
}
```

### Delete a collection

#### Endpoint

DELETE /collection/{collection_uuid}/

#### Description

Delete a collection

#### Parameters

- collection_uuid (UUID): The uuid of the collection.

#### Response

- Status Code: 204 NOT FOUND

### Get the current request count

#### Endpoint

GET /request-count/

#### Description

Get the current request count

#### Example

```bash
GET /request-count/
```

#### Response

- Status Code: 200 OK

#### Response Body:

```json
Response:
{
    "requests": "<number of requests served by this server till now>"
}
```

### Reset the request counter

#### Endpoint

POST /request-count/reset/

#### Description

Reset the request counter

#### Example

```bash
POST /request-count/reset/
```

#### Response

- Status Code: 200 OK

#### Response Body:

```json
{
    "message": "Request count reset successfully"
}
```

## Conclusion

This document provides a detailed overview of the Movie Collection App API endpoints along with usage examples.
