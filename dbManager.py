from database import Store


# Includes methods to ensure user inputs are valid before accessing the database
class Checks:
    # Checks user input when a user is attempting to sign up
    @staticmethod
    def valid_signup(session, username, password, store_name, street, city, state, country, zip):
        if (username is None or password is None or store_name is None or street is None or city is None or state is None
                or country is None or zip is None):
            print("a paramter is none")
            return False
        if session.query(Store).filter_by(username=username).first() is not None:
            print("username not unique")
            return False
        if session.query(Store).filter_by(street=street,city=city,state=state,country=country,zip=zip).first() is not None:
            print("address not unique")
            return False
        return True
