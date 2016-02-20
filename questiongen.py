from pint import UnitRegistry

from app.app import create_app
from app.models import NumericQuestion

app = create_app()

def numeric(quantity, fromValue, fromUnit, toUnit):
    ureg = UnitRegistry()

    from_q = ureg.Quantity(fromValue, fromUnit)
    to_q = ureg.Quantity(1, toUnit)

    res = from_q.to(to_q)
    print(str(res))
    print(ureg(str(res)).magnitude)

    #question = NumericQuestion(imagePath="blabla")

    ureg.define('Euro = [currency] = eur = EUR')
    


numeric("length", 5, "meter", "centimeter")
