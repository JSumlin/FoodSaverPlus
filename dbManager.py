from database import Store


# Includes methods to ensure user inputs are valid before accessing the database
class Checks:
    # Checks user input when a user is attempting to sign up
    @staticmethod
    def valid_signup(session, username, password, store_name, street, city, state, country, zip):
        if (username is None or password is None or store_name is None or street is None or city is None or state is None
                or country is None or zip is None):
            return False
        if not Checks.valid_username(session, username):
            return False
        if not Checks.valid_address(session, street, city, state, country, zip):
            return False
        return True

    @staticmethod
    def valid_username(session, username):
        if session.query(Store).filter_by(username=username).first() is not None:
            return False
        return True

    @staticmethod
    def valid_address(session, street, city, state, country, zip):
        if session.query(Store).filter_by(street=street,city=city,state=state,country=country,zip=zip).first() is not None:
            return False
        return True

    @staticmethod
    def valid_login(session, username, password):
        if username is None or password is None:
            return False
        store = session.query(Store).filter_by(username=username).first()
        if store is None:
            return False
        return store.verify_password(password)
