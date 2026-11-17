import unittest
from pydantic import ValidationError
from app.main import Dish, valid_id

class MenuValidationTests(unittest.TestCase):
    def test_restaurant_uuid_is_normalized(self):
        self.assertEqual(valid_id("10000000-0000-4000-8000-000000000001"), "10000000-0000-4000-8000-000000000001")
    def test_invalid_restaurant_id_is_rejected(self):
        from fastapi import HTTPException
        with self.assertRaises(HTTPException) as error: valid_id("not-a-uuid")
        self.assertEqual(error.exception.status_code, 400)
    def test_price_must_be_positive(self):
        with self.assertRaises(ValidationError):
            Dish(id="d", restaurante_id="r", nombre="Plato", descripcion="", categoria="Fondo", precio=0, imagen_url="https://example.test/p.jpg")

if __name__ == "__main__": unittest.main()
