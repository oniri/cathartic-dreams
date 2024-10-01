import concurrent.futures
from abc import ABC, abstractmethod

import llms
from files import read_file, load_json
from llms import chat_response


class AgentInterface(ABC):
    @abstractmethod
    def get_classification(self, dream, show_logs=True):
        pass


class BasicAgent(AgentInterface):
    def __init__(self, name, prompt_file, model='gpt-4o'):
        self.name = name
        self.model = model
        self.prompt = read_file(f"prompts/{prompt_file}.txt")

    def __str__(self):
        return f"BasicAgent {self.name}"

    def get_classification(self, dream, show_logs=True):
        prompt_with_dream = self.prompt.replace("[DREAM]", dream)
        response = chat_response(prompt_with_dream, model=self.model, json=True)

        if "classification" not in response:
            print(f"Classification response has invalid format: {response}")
            return None

        if isinstance(response["classification"], list):
            response["classification"] = response["classification"][0]

        if show_logs:
            print(f"{self.name} a décidé : {response['classification']}")
            print(f"Raison: {response['raison']}")
            print("----")

        response['agent'] = self.name
        return response


class MajorityCompoundAgent(AgentInterface):
    def __init__(self, name, agents):
        self.name = name
        self.agents = agents

    def __str__(self):
        return f"MajorityCompoundAgent {self.name}"

    def get_classification(self, dream, show_logs=True):
        results = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(agent.get_classification, dream, show_logs): agent for agent in self.agents}

            for future in concurrent.futures.as_completed(futures):
                try:
                    resultat = future.result()
                    results.append(resultat)
                except Exception as exc:
                    print(f"Classification generated an exception: {exc}")

        all_classifications = [result["classification"] for result in results if result]
        if not all_classifications:
            return {"classification": None}

        most_common_classification = max(set(all_classifications), key=all_classifications.count)
        confiance = all_classifications.count(most_common_classification) / len(all_classifications)

        if show_logs:
            print(f"{self.name} a décidé par majorité : {most_common_classification}")
            print("----")

        agents = {result['agent']: result for result in results}
        for agent in agents.values():
            del agent['agent']

        return {
            "class": most_common_classification,
            "confiance": confiance,
            "agents": agents,
        }


class SmartCompoundAgent(AgentInterface):
    def __init__(self, name, prompt_file, agents, helpers, model='gpt-4o'):
        self.name = name
        self.prompt = read_file(f"prompts/{prompt_file}.txt")
        self.agents = agents
        self.helpers = helpers
        self.model = model


    def __str__(self):
        return f"SmartCompoundAgent {self.name}"

    def get_classification(self, dream, show_logs=True):
        agent_results = []
        helper_reports = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(agent.get_classification, dream, show_logs): agent for agent in self.agents}

            for future in concurrent.futures.as_completed(futures):
                try:
                    resultat = future.result()
                    agent_results.append(resultat)
                except Exception as exc:
                    print(f"Classification generated an exception: {exc}")

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(helper.generate_report, dream): helper for helper in self.helpers}

            for future in concurrent.futures.as_completed(futures):
                try:
                    report = future.result()
                    helper_reports.append(report)
                except Exception as exc:
                    print(f"Helper report generated an exception: {exc}")

        filled_prompt = self.prompt.replace("[DREAM]", dream)

        answers_descriptions = [f"Agent {r['agent']} a décidé : {r['classification']}\nRaison: {r['raison']}" for r in agent_results if r]
        filled_prompt = filled_prompt.replace("[ANSWERS]", "\n\n".join(answers_descriptions))

        helper_reports = [f"\"{r}\"" for r in helper_reports if r]
        filled_prompt = filled_prompt.replace("[HELPERS]", "\n\n".join(helper_reports))

        final_response = chat_response(filled_prompt, model=self.model, json=True)

        if show_logs:
            print(f"{self.name} a décidé : {final_response['classification']}")
            print(f"Raison: {final_response['raison']}")
            print("----")

        return {
            "classification": final_response.get("classification"),
            "raison": final_response['raison'],
            "agent": self.name
        }


class ProbaAgent(AgentInterface):
    def __init__(self, name, prompt_file, model='gpt-4o'):
        self.name = name
        self.model = model
        self.prompt = read_file(f"prompts/{prompt_file}.txt")

    def __str__(self):
        return f"ProbaAgent {self.name}"

    def get_classification(self, dream, show_logs=True):
        prompt_with_dream = self.prompt.replace("[DREAM]", dream)
        response = chat_response(prompt_with_dream, model=self.model, json=True)

        if "classifications" not in response:
            print(f"Classification response has invalid format: {response}")
            return None

        if show_logs:
            print(f"{self.name} : {response['classifications']}")
            print("----")

        response['agent'] = self.name
        return response


class CompoundProbaAgent(AgentInterface):
    def __init__(self, name, agents):
        self.name = name
        self.agents = agents

    def __str__(self):
        return f"CompoundProbaAgent {self.name}"

    def get_classification(self, dream, show_logs=True):
        results = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(agent.get_classification, dream, show_logs): agent for agent in self.agents}

            for future in concurrent.futures.as_completed(futures):
                try:
                    resultat = future.result()
                    results.append(resultat)
                except Exception as exc:
                    print(f"Classification generated an exception: {exc}")

        all_classifications = [result["classifications"] for result in results if result]
        if not all_classifications:
            return {"classifications": None}

        # sum values
        total = {}
        for classification in all_classifications:
            for key, value in classification.items():
                total[key] = total.get(key, 0) + value

        # get key with max value
        main_classification = max(total, key=total.get)

        return {
            "class": main_classification,
            "classifications": total,
        }


class Helper:
    def __init__(self, id, prompt_file):
        self.id = id
        self.prompt = read_file(f"prompts/{prompt_file}.txt")

    def generate_report(self, dream):
        filled_prompt = self.prompt.replace("[DREAM]", dream)
        response = chat_response(filled_prompt)

        print(f"{self.id}:\n{response}")

        return response


