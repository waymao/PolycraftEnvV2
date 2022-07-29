from gym_novel_gridworlds2.contrib.polycraft.objects.polycraft_obj import PolycraftObject


class IronOre(PolycraftObject):
    def __init__(self, typee, loc=(0, 0), state="floating", **kwargs):
        self.type = typee
        self.loc = loc  # update such that we update the 3D arr and add the item to it
        self.state = state  # two states: block and floating

    def placement_reqs(self, map_state, loc):
        return True

    def acted_upon(self, action_name, agent):
        if action_name == "break":
            self.state = "floating"
            # if "diamond" in agent.inventory:
            #     agent.inventory["diamond"] += 9
            # else:
            #     agent.inventory.update({"diamond": 9})
