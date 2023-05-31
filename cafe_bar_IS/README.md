# Cafe and Bar Information System

## How to run

- `git clone https://github.com/KazimierasJasaitis/cafe_bar_info_system_V2.git`
- `cd cafe_bar_info_system_V2`
- `docker-compose up`

## API Endpoints available on port 80
### Users

- `POST /user`: Create a new user.
- `GET /user`: Get a list of all users.
- `GET /user/<username>`: Get a specific user by username.
- `PUT /user/<username>`: Update a user by username.
- `DELETE /user/<username>`: Delete a user by username.

### BarCafe

- `POST /bar_cafe`: Create a new bar/cafe.
- `GET /bar_cafe`: Get a list of all bars/cafes.
- `GET /bar_cafe/<id>`: Get a specific bar/cafe by ID.
- `PUT /bar_cafe/<id>`: Update a bar/cafe by ID.
- `DELETE /bar_cafe/<id>`: Delete a bar/cafe by ID.

### SeatStatus

- `POST /seat_status`: Create a new seat status.
- `GET /seat_status`: Get a list of all seat statuses.
- `GET /seat_status/<id>`: Get a specific seat status by ID.
- `PUT /seat_status/<id>`: Update a seat status by ID.
- `DELETE /seat_status/<id>`: Delete a seat status by ID.

### KarmaLog

- `POST /karma_log`: Create a new karma log.
- `GET /karma_log`: Get a list of all karma logs.
- `GET /karma_log/<id>`: Get a specific karma log by ID.
- `PUT /karma_log/<id>`: Update a karma log by ID.
- `DELETE /karma_log/<id>`: Delete a karma log by ID.

###

- `POST /bar_cafe/<id>/menu`: Create a new dish for the menu of the cafe specified by ID.
- `GET /bar_cafe/<id>/menu`: Get the menu for the cafe specified by ID.
- `GET /dishes`: Get all available dishes.