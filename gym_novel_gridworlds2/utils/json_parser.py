import json
import importlib
from re import L
from typing import Mapping, Tuple, Type

from .MultiAgentActionSpace import MultiAgentActionSpace

from ..object import Object, Entity
from ..actions import ActionSet, Action
from ..state.dynamic import Dynamic
from ..agents import Agent


from ..contrib.polycraft.actions.craft import Craft
from ..state import State


class ParseError(Exception):
    pass


def import_module(module_path: str):
    module_file_path, class_name = module_path.rsplit('.', 1)
    file_module = importlib.import_module(module_file_path)
    class_module = getattr(file_module, class_name)
    return class_module



class ConfigParser:
    def __init__(self) -> None:
        self.obj_types = {}
    
    def parse_json(self, json_file_name) -> Tuple[State, Dynamic, dict]:
        json_content = None
        with open(json_file_name, "r") as f:
            json_content = json.load(f, strict=False)
        
        # state
        self.state = State(
            map_size=tuple(json_content['map_size']),
        )

        # actions
        self.actions = {}
        for key, action_info in json_content['actions'].items():
            self.actions[key] = self.create_action(action_info)

        # object types
        self.parse_object_types(json_content['object_types'])

        # placement of objects on the map
        for obj_name, locs in json_content['objects'].items():
            self.create_place_obj(self.state, obj_name, locs)

        # recipe
        self.parse_recipe(json_content['recipes'])
        
        # action sets
        self.action_sets = {}
        for key, action_list in json_content['action_sets'].items():
            self.action_sets[key] = self.create_action_set(action_list)
        
        # entities
        self.entities: Mapping[str, dict] = {}
        for key, entity_info in json_content['entities'].items():
            self.entities[key] = self.create_place_entity(
                name=key,
                entity_info=entity_info
            )
        
        action_space = MultiAgentActionSpace([e['action_set'].get_action_space() for name, e in self.entities.items()])
        
        # TODO: separate out recipes?
        dynamic = Dynamic(
            actions=self.actions,
            action_sets=self.action_sets, 
            action_space=action_space,
            obj_types=self.obj_types)
        return (self.state, dynamic, self.entities)

    
    def parse_recipe(self, state: State, recipe_dict):
        self.state = state
        self.actions = {}
        items = list(recipe_dict.keys())
        for i in range(len(items)):
            craftStr = "craft_" + items[i]
            self.actions[craftStr] = Craft(state=self.state, recipe=recipe_dict[items[i]])
            return self.actions


    def parse_object_types(self, obj_types_info: dict):
        """
        Given a dict of something like
        "default": "some_module.object_module",
        """
        self.obj_types = {}
        for key, info in obj_types_info.items():
            if type(info) == str:
                self.obj_types[key] =  {
                    "module": import_module(info),
                    "params": {}
                }
            else:
                self.obj_types[key] =  {
                    "module": import_module(info),
                    "params": info['params']
                }

    def create_place_obj(self, state: State, obj_name, obj_locs):
        """
        Given a name, creates an object using the correct name
        """
        obj_type_info = self.obj_types.get(obj_name) or self.obj_types['default']
        ObjectModule: Object = obj_type_info['module']
        for loc in obj_locs:
            state.place_object(
                obj_name, 
                ObjectModule, 
                properties={"loc": loc, **obj_type_info['params']}
            )


    def create_action(self, action_info):
        ActionModule: Type[Action] = import_module(action_info['module'])
        del action_info['module']
        try:
            action = ActionModule(state=self.state, **action_info)
        except TypeError as e:
            raise ParseError(
                f"Module {ActionModule.__name__} initialization error: " + \
                str(e))
        return action

    def create_action_set(self, action_str_list):
        action_list = []
        for action_str in action_str_list:
            action_list.append(self.actions[action_str])
        return ActionSet(action_list)

    def create_place_entity(self, name: str, entity_info: dict):
        AgentClass: Type[Agent] = import_module(entity_info['agent'])
        EntityClass: Type[Entity] = import_module(entity_info['entity'])

        # action set
        try:
            action_set_name = entity_info['action_set']
            action_set: ActionSet = self.action_sets[action_set_name]
        except KeyError as e:
            raise ParseError(f'Action Set {action_set_name} not found in config') from e
        
        # entity object
        info = entity_info.copy()
        del info['agent']
        del info['entity']
        del info['action_set']
        entity_obj = self.state.place_object(entity_info['type'], EntityClass, entity_info)

        # agent object
        agent_obj = AgentClass(name=name, action_space=action_set.get_action_space())
        return {
            "action_set": action_set,
            "agent": agent_obj,
            "entity": entity_obj
        }
