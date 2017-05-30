from task import db


class Purchase(db.Model):
    """
    Simple model for purchase object
    """
    id = db.Column(db.Integer, primary_key=True)
    purchase_hash = db.Column(db.String(255), unique=True)
    card_token = db.Column(db.String(255), unique=True)
    operation = db.Column(db.String(80))
    email = db.Column(db.String(80))
    name = db.Column(db.String(80))
    country = db.Column(db.String(80))
    document = db.Column(db.String(80))
    zipcode = db.Column(db.Integer)
    address = db.Column(db.String(80))
    street_number = db.Column(db.Integer)
    city = db.Column(db.String(80))
    state = db.Column(db.String(80))
    phone_number = db.Column(db.Integer)
    birth_date = db.Column(db.String(80))
    currency_code = db.Column(db.String(80))
    amount_total = db.Column(db.Float)
    payment_type_code = db.Column(db.String(80))

    def __init__(self, operation, email, name,
                 country, document, zipcode, address, street_number, city,
                 state, phone_number, birth_date, currency_code,
                 amount_total, payment_type_code,
                 card_token='', purchase_hash=''):

        self.purchase_hash = purchase_hash
        self.card_token = card_token
        self.operation = operation
        self.email = email
        self.name = name
        self.country = country
        self.document = document
        self.zipcode = zipcode
        self.address = address
        self.street_number = street_number
        self.city = city
        self.state = state
        self.phone_number = phone_number
        self.birth_date = birth_date
        self.currency_code = currency_code
        self.amount_total = amount_total
        self.payment_type_code = payment_type_code

    def __str__(self):
        return "Purchase %d" % self.id
