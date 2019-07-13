class Organization:
    """
    Organizations come in two varities: Companies or NGOs
    Generally companies will negatively affect the planet
    while NGOs / non-profits will have positive affects
    """

    def __init__(self, name: str, ceo: str, description: str) -> None:
        self.name = name
        self.ceo = ceo
        self.description = description

    def __str__(self) -> str:
        summary = f"{self.name}\nCEO: {self.ceo}\n{self.description}\n"
        return summary
