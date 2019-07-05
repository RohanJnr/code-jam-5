from typing import List
from .news import News
from .organization import Organization
from .policy import Policy


class Investment:
    """
    Investments are choices presented to the player on how they
    allocate their money. Investements will have a positive, negative
    or possiblely no affect on the planet and could generate news, ROI funds
    or unlock new investment opportunities in future rounds.
    """

    def __init__(
        self,
        organization: Organization,
        policies: List[Policy],
        roi: float = 0.0,
        news_on_apperance: List[News] = None,
        news_on_investment: List[News] = None,
        news_on_no_investment: List[News] = None,
    ) -> None:
        self.organization = organization
        self.policies = policies
        self.news_on_apperance = news_on_apperance
        self.news_on_investment = news_on_investment
        self.news_on_no_investment = news_on_no_investment
        self.roi = roi
        self.times_invested = 0

    def __str__(self) -> str:
        output = (
            f"{str(self.organization)}\nROI: {self.roi}\n\n{str(self.current_policy)}"
        )
        return output

    @property
    def current_policy(self):
        return self.policy[self.times_invested]
