from attr import dataclass

from ChefkochContracts import ChefkochEntity


@dataclass
class ParsingResult:
    entity: ChefkochEntity
    foundRecipes: list[str]
    foundCategories: list[str]