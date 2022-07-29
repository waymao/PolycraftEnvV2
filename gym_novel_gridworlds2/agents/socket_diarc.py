from ast import Mult
from typing import Optional
import numpy as np
from gym.spaces import Discrete, Dict, MultiDiscrete, Box
import json

from gym_novel_gridworlds2.state.dynamic import Dynamic

from .socket_agent import SocketManualAgent

def sense_all(state):
    pass

class SocketDiarcAgent(SocketManualAgent):
    def __init__(self, **kwargs):
        self.state_cache = None
        self.dynamics_cache: Optional[Dynamic] = None
        super().__init__(**kwargs)

    def get_observation_space(self, map_size: tuple, other_size: int):
        return Discrete(1) # dummy observation space to bypass sanity check
    
    def get_observation(self, state, dynamics):
        self.state_cache = state
        self.dynamics_cache = dynamics
        return super().get_observation(state, dynamics)
    
    def policy(self, observation):
        # process the sense_all commands
        action_done = False
        while not action_done:
            action = self._recv_msg()
            if action.startswith("SENSE"):
                self.action_set.parse_exec_command(action)
            else:
                self.action_set.parse_exec_command(action)
        return 0
    
    def update_metadata(self, metadata: dict):
        if type(metadata) == dict:
            msg = json.dumps(metadata + "\n")
        else:
            msg = metadata
        self._send_msg(json.dumps(msg))
