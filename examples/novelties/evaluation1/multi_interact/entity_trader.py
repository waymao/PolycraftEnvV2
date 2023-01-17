from gym_novel_gridworlds2.contrib.polycraft.objects import EntityTrader

class EntityTraderMultInteract(EntityTrader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.interact_count = 0
    
    def acted_upon(self, action_name, agent):
        # interact, break, use, etc
        if action_name == "interact":
            if self.interact_count % 3 == 2:
                agent.add_to_inventory("oak_log", 9)
            self.interact_count += 1
            print("interact count: ", self.interact_count)