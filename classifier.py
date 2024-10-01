import concurrent.futures
import pandas as pd
from openpyxl.styles import Alignment
from openpyxl.utils import get_column_letter


def flatten_data(data, parent_key=''):
    items = {}
    for key, value in data.items():
        new_key = parent_key + ('.' if parent_key else '') + key
        if isinstance(value, dict):
            items.update(flatten_data(value, new_key))
        else:
            items[tuple(new_key.split('.'))] = value
    return items


def get_model_output(agent, df, limit=None, recit_column='recit'):
    outputs = {}
    counter = 0

    limited_df = df.head(limit) if limit else df

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(agent.get_classification, row[recit_column], show_logs=False): index for index, row in limited_df.iterrows()}

        for future in concurrent.futures.as_completed(futures):
            index = futures[future]
            result = future.result()
            outputs[index] = result

            counter += 1
            print(f"{counter}/{len(df)}")

    return outputs


def format_output(original_df, outputs):
    new_columns = []
    new_data = []

    for index, output in outputs.items():
        row_data = flatten_data(output)

        # fix length of tuples to all have the max length
        max_length = max([len(col) for col in row_data.keys()])
        fixed_row_data = {}
        for col in row_data:
            if len(col) < max_length:
                fixed_row_data[tuple(list(col) + [''] * (max_length - len(col)))] = row_data[col]
            else:
                fixed_row_data[col] = row_data[col]

        for col in fixed_row_data.keys():
            if col not in new_columns:
                new_columns.append(col)

        new_data.append(fixed_row_data)

    new_df = pd.DataFrame(new_data, index=outputs.keys()).reindex(columns=pd.MultiIndex.from_tuples(new_columns))

    # Add existing columns from the original DataFrame
    for col in reversed(original_df.columns):
        if col not in new_df.columns:
            new_df.insert(0, col, original_df[col])

    # Sort the DataFrame by its index to ensure the rows are in the correct order
    new_df.sort_index(inplace=True)

    return new_df


def write_output_to_file(df, output_path: str):
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Results')

        # Adjust column widths for readability and add text wrapping
        # worksheet = writer.sheets['Results']
        # for col_idx, col in enumerate(worksheet.columns, 1):
        #     max_length = 0
        #     col_letter = get_column_letter(col_idx)  # Get the column letter
        #     for cell in col:
        #         cell.alignment = Alignment(wrap_text=True)  # Add text wrapping
        #         try:
        #             if len(str(cell.value)) > max_length:
        #                 max_length = len(str(cell.value))
        #         except:
        #             pass
        #     adjusted_width = min(max_length + 2, 60)  # Set maximum column width
        #     worksheet.column_dimensions[col_letter].width = adjusted_width


def apply_model_to_file(agent, input_file: str, output_path: str, limit=None, subset=None, recit_column='recit', key_columns=['id']):
    df = pd.read_excel(input_file, engine='openpyxl')
    df = df[df[recit_column].notna()]

    # Filter the dataframe if a subset is provided (list of keys participant-reve)
    if subset:
        for index, row in df.iterrows():
            key = [row[col] for col in key_columns].join('-')
            if key not in subset:
                df.drop(index, inplace=True)


    outputs = get_model_output(agent, df, limit=limit, recit_column=recit_column)
    new_df = format_output(df, outputs)
    write_output_to_file(new_df, output_path)