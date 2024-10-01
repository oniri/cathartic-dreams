from agents import BasicAgent, MajorityCompoundAgent
from classifier import apply_model_to_file


agent_ZA_9 = MajorityCompoundAgent("ZA_9", [
    BasicAgent("1", "prompt_7", model='gpt-4o'),
    BasicAgent("2", "prompt_7", model='gpt-4o'),
    BasicAgent("3", "prompt_7", model='gpt-4o'),
    BasicAgent("4", "prompt_7", model='gpt-4o'),
    BasicAgent("5", "prompt_7", model='gpt-4o'),
    BasicAgent("6", "prompt_7", model='gpt-4o'),
    BasicAgent("7", "prompt_7", model='gpt-4o'),
    BasicAgent("8", "prompt_7", model='gpt-4o'),
    BasicAgent("9", "prompt_7", model='gpt-4o'),
])


if __name__ == '__main__':
    apply_model_to_file(
        agent_ZA_9,
        'input/your_input_file.xlsx',
        'output/output.xlsx',
        key_columns=['id1', 'id2'],
        recit_column='text'
    )