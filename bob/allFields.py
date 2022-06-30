from typing import Iterable

from bob.field import Field
from bob.basicField import BasicField
from bob.temperature import Temperature
from bob.combinedField import CombinedField


def addFields(fields: Iterable[Field]) -> None:
    for field in fields:
        allFields.append(field)


allFields = [
    BasicField("Density", None),
    BasicField("Masses", None),
    BasicField("Coordinates", None),
    BasicField("InternalEnergy", None),
    Temperature(),
]

addFields(BasicField("ChemicalAbundances", i) for i in range(6))
addFields(CombinedField([BasicField("Density"), BasicField("ChemicalAbundances", i)]) for i in range(6))
addFields(BasicField("PhotonRates", i) for i in range(5))
addFields(BasicField("PhotonFlux", i) for i in range(5))
addFields(BasicField("SGCHEM_HeatCoolRates", i) for i in range(12))


def getFieldByName(name: str) -> Field:
    return next(field for field in allFields if field.niceName == name)
