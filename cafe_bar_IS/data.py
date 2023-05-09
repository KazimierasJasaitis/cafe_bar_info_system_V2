def populate_initial_data(session, User, BarCafe, SeatStatus, KarmaLog):
    if session.query(User).count() == 0:
        initial_users = [
            {
                "username": "john",
                "password": "password123",
                "email": "john@example.com",
                "role": "admin",
                "managed_cafe_id": None,
                "reputation_index": 10,
            },
            {
                "username": "jane",
                "password": "password456",
                "email": "jane@example.com",
                "role": "user",
                "managed_cafe_id": None,
                "reputation_index": 5,
            },
        ]

        for data in initial_users:
            user = User(**data)
            session.add(user)

    if session.query(BarCafe).count() == 0:
        initial_bar_cafes = [
            {
                "name": "Coffee spells",
                "location": "Pylimo g. 38C",
                "open_hours": "08:00-17:00",
                "type": "cafe",
                "seats": 18,
                "user_id": "john"
            },
            {
                "name": "Local pub",
                "location": "J. Jasinskio g. 1",
                "open_hours": "16:00-00:00",
                "type": "bar",
                "seats": 25,
                "user_id": "jane"
            },
            {
                "name": "Lola",
                "location": "Naugarduko g. 2A",
                "open_hours": "8:00-18:00",
                "type": "cafe",
                "seats": 40,
                "user_id": "john"
            },
        ]

        for data in initial_bar_cafes:
            bar_cafe = BarCafe(**data)
            session.add(bar_cafe)

    if session.query(SeatStatus).count() == 0:
        initial_seat_statuses = [
            {
                "bar_cafe_id": 1,
                "user_id": "john",
                "status": "occupied",
                "timestamp": "2023-05-01T10:00:00",
            },
            {
                "bar_cafe_id": 2,
                "user_id": "jane",
                "status": "vacant",
                "timestamp": "2023-05-01T11:00:00",
            },
        ]

        for data in initial_seat_statuses:
            seat_status = SeatStatus(**data)
            session.add(seat_status)

    if session.query(KarmaLog).count() == 0:
        initial_karma_logs = [
            {
                "user_id": "john",
                "karma_points": 5,
                "timestamp": "2023-05-01T12:00:00",
            },
            {
                "user_id": "jane",
                "karma_points": -3,
                "timestamp": "2023-05-01T13:00:00",
            },
        ]

        for data in initial_karma_logs:
            karma_log = KarmaLog(**data)
            session.add(karma_log)

    session.commit()

