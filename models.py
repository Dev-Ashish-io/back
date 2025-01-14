from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    money = db.Column(db.Float, nullable=False, default=500000)
    stocks = db.Column(db.JSON, nullable=False, default={})

    def update_stock(self, stock_name, quantity, price, action):
        cost = price * quantity
        if action == 'buy':
            if cost > self.money:
                raise ValueError("Not enough money to buy stocks.")
            self.money -= cost
            self.stocks[stock_name] = self.stocks.get(stock_name, 0) + quantity
        elif action == 'sell':
            if self.stocks.get(stock_name, 0) < quantity:
                raise ValueError("Not enough stocks to sell.")
            self.money += cost
            self.stocks[stock_name] -= quantity

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'money': self.money, 'stocks': self.stocks}

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    stock_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    action = db.Column(db.String(10), nullable=False)
