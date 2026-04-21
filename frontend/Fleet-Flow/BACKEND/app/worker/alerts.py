def check_low_stock(db):
    low_items = db.query(Inventory).filter(Inventory.quantity < 10).all()
    return low_items