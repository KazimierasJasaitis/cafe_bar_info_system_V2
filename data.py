def populate_initial_data(session, CafeBar):
    if session.query(CafeBar).count() == 0:
        initial_data = [
            {
                "name": "Coffee spells",
                "location": "Pylimo g. 38C",
                "open_hours": "08:00-17:00",
                "type": "cafe",
                "seats": 18,
            },
            {
                "name": "Local pub",
                "location": "J. Jasinskio g. 1",
                "open_hours": "16:00-00:00",
                "type": "bar",
                "seats": 25,
            },
            {
                "name": "Lola",
                "location": "Naugarduko g. 2A",
                "open_hours": "8:00-18:00",
                "type": "cafe",
                "seats": 40,
            },
        ]

        for data in initial_data:
            cafe_bar = CafeBar(**data)
            session.add(cafe_bar)

        session.commit()
