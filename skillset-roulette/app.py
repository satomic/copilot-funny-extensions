import random

class RouletteGame:
    def __init__(self, prize_dict):
        # Roulette options
        self.prize_dict = prize_dict
        self.options = list(prize_dict.keys())
        self.winners = []
        self.thanks = "thanks"
        self.probabilities = self.calculate_probabilities()

    def calculate_probabilities(self):
        total_index = sum(prize["index"] for prize in self.prize_dict.values())
        probabilities = {prize: prize_info["index"] / total_index for prize, prize_info in self.prize_dict.items()}
        return probabilities

    def spin(self, player_name):
        """Simulate roulette spin and return result"""
        result = random.choices(self.options, weights=self.probabilities.values(), k=1)[0]
        if result != self.thanks:
            self.winners.append({"name": player_name, "prize": result})
        return result

    def get_winners(self):
        """Return all winners"""
        return self.winners