from gym_novel_gridworlds2.contrib.polycraft.objects import PolycraftEntity, PolycraftObject
from gym_novel_gridworlds2.actions.action import PreconditionNotMetError

class BirchTree(PolycraftObject):
    def acted_upon(self, action_name, agent: PolycraftEntity):
        if action_name == "break":
            if agent.selectedItem == "axe":
                self.state = "floating" # tree can only be broken with axe selected
            else:
                raise PreconditionNotMetError("You need to select an axe to break this tree")
        super().acted_upon(action_name, agent)