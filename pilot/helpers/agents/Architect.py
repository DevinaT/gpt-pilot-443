from utils.utils import step_already_finished
from helpers.Agent import Agent
import json
from utils.style import color_green_bold
from const.function_calls import ARCHITECTURE

from utils.utils import should_execute_step, generate_app_data
from database.database import save_progress, get_progress_steps
from logger.logger import logger
from helpers.AgentConvo import AgentConvo

ARCHITECTURE_STEP = 'architecture'


class Architect(Agent):
    def __init__(self, project):
        super().__init__('architect', project)
        self.convo_architecture = None

    def get_architecture(self):
        print(json.dumps({
            "project_stage": "architecture"
        }), type='info')

        self.project.current_step = ARCHITECTURE_STEP

        def is_architecture_step_already_finished(project):
            step = get_progress_steps(project.args['app_id'], ARCHITECTURE_STEP)
            return step and not should_execute_step(project.args['step'], ARCHITECTURE_STEP)

        def handle_finished_architecture_step(project, step):
            step_already_finished(project.args, step)
            project.architecture = step['architecture']
            return

        if is_architecture_step_already_finished(self.project):
            handle_finished_architecture_step(self.project, step)
            return

        # ARCHITECTURE
        print(color_green_bold("Planning project architecture...\n"))
        logger.info("Planning project architecture...")

        self.convo_architecture = AgentConvo(self)
        llm_response = self.convo_architecture.send_message('architecture/technologies.prompt',
            {'name': self.project.args['name'],
             'prompt': self.project.project_description,
             'clarifications': self.project.clarifications,
             'user_stories': self.project.user_stories,
             'user_tasks': self.project.user_tasks,
             'app_type': self.project.args['app_type']}, ARCHITECTURE)
        self.project.architecture = llm_response['technologies']

        # TODO: Project.args should be a defined class so that all of the possible args are more obvious
        if self.project.args.get('advanced', False):
            llm_response = self.convo_architecture.get_additional_info_from_user(ARCHITECTURE)
            if llm_response is not None:
                self.project.architecture = llm_response['technologies']

        logger.info(f"Final architecture: {self.project.architecture}")

        save_progress(self.project.args['app_id'], self.project.current_step, {
            "messages": self.convo_architecture.messages,
            "architecture": self.project.architecture,
            "app_data": generate_app_data(self.project.args)
        })

        return
        # ARCHITECTURE END
