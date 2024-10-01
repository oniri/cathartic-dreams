# How to use

1. Create a file named `.env` and add the following:

```bash
OPENAI_API_KEY=your-api-key
```
Your API key can be found in the [OpenAI dashboard](https://platform.openai.com/login).


2. Install the dependencies:

```bash
pip install -r requirements.txt
```


3. Add the input file with the dreams to classify, e.g. `dreams.xlsx`. Each dream must be in a separate row. There must be one or more columns to uniquely identify each dream, e.g. `partipant_id`+`dream_id`, and one column with the dream text, e.g. `text`.


4. Run `main.py`, adjusting the parameters passed to `apply_model_to_file`.


If you have any questions, please write to [contact@oniri.io](mailto:contact@oniri.io).